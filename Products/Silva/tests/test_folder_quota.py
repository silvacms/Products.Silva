# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Products.Silva import File
from Products.Silva.Publication import OverQuotaException
from Products.Silva.testing import FunctionalLayer, TestRequest, Transaction
from silva.core.xml import ZipImporter
from silva.core.interfaces import IArchiveFileImporter, IAsset, IPublication
from silva.core.interfaces import IContainerManager
from silva.core.services.interfaces import IExtensionService, IMetadataService


def set_quota(content, size_in_megabytes):
    if not IPublication.providedBy(content):
        raise ValueError('cannot set quota content on %r' % content)
    service = getUtility(IMetadataService)
    binding = service.getMetadata(content)
    binding.setValues('silva-quota', {'quota': size_in_megabytes})


class ActivationQuotaTestCase(unittest.TestCase):
    """Test quota system activate/desactivation.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_activation(self):
        """Test that we can disable the extension.  After, create some
        content (same structure than the test folderAction), activate
        it, and check that all values are updated.
        """
        # The quota is disabled by default
        service = getUtility(IExtensionService)
        self.assertEqual(service.get_quota_subsystem_status(), None)
        self.assertEqual(service.get_site_quota(), 0)

        # You can enable it.
        self.assertEqual(service.enable_quota_subsystem(), True)
        self.assertEqual(service.get_quota_subsystem_status(), True)

        # Enabling the already enabled service won't change anything.
        self.assertEqual(service.enable_quota_subsystem(), False)
        self.assertEqual(service.get_quota_subsystem_status(), True)

        # And disabled it.
        self.assertEqual(service.disable_quota_subsystem(), True)
        self.assertEqual(service.get_quota_subsystem_status(), None)

        # If you disable it again you will get False and nothing will change.
        self.assertEqual(service.disable_quota_subsystem(), False)
        self.assertEqual(service.get_quota_subsystem_status(), None)

    def test_activation_with_site_quota(self):
        """If you set a site quota and activate the feature, you won't
        be able to disable it (unless you clear the site quota).
        """
        service = getUtility(IExtensionService)
        self.assertEqual(service.get_quota_subsystem_status(), None)

        # Enable with site_quota.
        service._site_quota = 100
        self.assertEqual(service.enable_quota_subsystem(), True)
        self.assertEqual(service.get_quota_subsystem_status(), True)
        self.assertEqual(service.get_site_quota(), 100)

        # Disable/enable won't change anything
        self.assertEqual(service.disable_quota_subsystem(), False)
        self.assertEqual(service.get_quota_subsystem_status(), True)
        self.assertEqual(service.enable_quota_subsystem(), False)
        self.assertEqual(service.get_quota_subsystem_status(), True)
        self.assertEqual(service.disable_quota_subsystem(), False)
        self.assertEqual(service.get_quota_subsystem_status(), True)

    def test_collect_quota_on_activation(self):
        """Test values update on activation.
        """
        # Create some content
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder1', 'FooFolder 1')
        factory.manage_addFolder('folder2', 'FooFolder 2')
        folder1 = self.root._getOb('folder1')
        folder2 = self.root._getOb('folder2')
        factory = folder1.manage_addProduct['Silva']
        factory.manage_addFolder('subfolder', 'Sub FooFolder')
        subfolder1 = folder1._getOb('subfolder')
        factory = subfolder1.manage_addProduct['Silva']
        with self.layer.open_fixture('test1.zip') as source:
            factory.manage_addFile('zipfile1.zip', 'Zip File', source)
            # After reading the file, position should be end of file
            zip1_size = source.tell()
        factory = folder2.manage_addProduct['Silva']
        with self.layer.open_fixture('torvald.jpg') as source:
            factory.manage_addImage('image1.jpg', 'Image File', source)
            image1_size = source.tell()

        # No counting should be done (extensions not activated)
        self.assertEqual(self.root.used_space, 0)
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(folder2.used_space, 0)

        # Activate the quota system
        self.root.service_extensions.enable_quota_subsystem()

        # Values should be updated
        self.assertEqual(self.root.used_space, zip1_size + image1_size)
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Disable
        self.root.service_extensions.disable_quota_subsystem()

        # Do some changes
        manager = IContainerManager(folder1)
        with manager.deleter() as deleter:
            deleter(folder1.subfolder)
        with manager.copier() as copier:
            copier(self.root.folder2)

        # Nothing had change
        self.assertEqual(self.root.used_space, zip1_size + image1_size)
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Re-enable
        self.root.service_extensions.enable_quota_subsystem()
        # Values should be updated
        self.assertEqual(self.root.used_space, (2 * image1_size))
        self.assertEqual(folder1.used_space, image1_size)
        self.assertEqual(folder2.used_space, image1_size)


class QuotaTestCase(unittest.TestCase):
    """Test quota system implementation.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        with Transaction():
            self.root = self.layer.get_application()
            self.root.service_files.storage = File.BlobFile
            self.root.service_extensions.enable_quota_subsystem()

        self.layer.login('editor')

    def test_validate_wanted_quota_on_publication(self):
        """Test validate wanted quota on a publication.
        Content structure:

        root
        `-- publication
            `-- folder
                `-- child
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication 1')
        publication = self.root.publication
        factory = publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder 1')
        folder = self.root.publication.folder
        factory = folder.manage_addProduct['Silva']
        factory.manage_addPublication('child', 'Publication 3')
        child = self.root.publication.folder.child

        # By default, the quota is 0
        self.assertEqual(publication.get_current_quota(), 0)
        self.assertEqual(child.get_current_quota(), 0)
        self.assertEqual(self.root.get_current_quota(), 0)

        # Wanted quota check if the wanted value is correct. Negative
        # is invalid. As well it can't be larger than the parent
        # one. But larger than the current value.
        self.assertFalse(publication.validate_wanted_quota(-10))
        self.assertTrue(publication.validate_wanted_quota(50))
        self.assertTrue(publication.validate_wanted_quota(0))

        set_quota(self.root, 20)
        self.assertFalse(publication.validate_wanted_quota(50))
        self.assertTrue(publication.validate_wanted_quota(0))
        self.assertTrue(self.root.validate_wanted_quota(30))

        set_quota(publication, 10)
        self.assertFalse(child.validate_wanted_quota(15))
        self.assertTrue(child.validate_wanted_quota(5))
        self.assertTrue(publication.validate_wanted_quota(15))

        # Values are of now:
        self.assertEqual(publication.get_current_quota(), 10)
        self.assertEqual(child.get_current_quota(), 10)
        self.assertEqual(self.root.get_current_quota(), 20)

        # You can reset a quota with 0
        set_quota(publication, 0)
        self.assertEqual(publication.get_current_quota(), 20)
        self.assertEqual(child.get_current_quota(), 20)
        self.assertEqual(self.root.get_current_quota(), 20)

    def test_validate_wanted_quota_on_root(self):
        """Test validate wanted quota on a root with conformity of the
        site quota.
        Content structure:

        root
        `-- publication
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication 1')
        publication = self.root.publication
        service = self.root.service_extensions

        # By default, the quota is 0 (disabled)
        self.assertEqual(publication.get_current_quota(), 0)
        self.assertEqual(self.root.get_current_quota(), 0)
        self.assertEqual(service.get_site_quota(), 0)

        # Set the site quota and check again to see all quota set to
        # the site one:
        service._site_quota = 20
        self.assertEqual(publication.get_current_quota(), 20)
        self.assertEqual(self.root.get_current_quota(), 20)
        self.assertEqual(service.get_site_quota(), 20)

        # You cannot set a quota on Root higher than the site quota:
        self.assertFalse(self.root.validate_wanted_quota(30))
        self.assertTrue(self.root.validate_wanted_quota(20))

        # Same for publication:
        self.assertFalse(publication.validate_wanted_quota(30))
        self.assertTrue(publication.validate_wanted_quota(20))

        # You can set smaller quota than the site quotas:
        set_quota(self.root, 15)
        set_quota(publication, 10)
        self.assertEqual(publication.get_current_quota(), 10)
        self.assertEqual(self.root.get_current_quota(), 15)
        self.assertEqual(service.get_site_quota(), 20)

        # And validate higher ones after:
        self.assertTrue(self.root.validate_wanted_quota(20))
        self.assertTrue(publication.validate_wanted_quota(15))

        # You can reset all quotas:
        set_quota(self.root, 0)
        set_quota(publication, 0)

        # And obtain the site quota again:
        self.assertEqual(publication.get_current_quota(), 20)
        self.assertEqual(self.root.get_current_quota(), 20)
        self.assertEqual(service.get_site_quota(), 20)

    def test_folder_action(self):
        """Test that folder action update used space.
        Content structure:

        root
        |-- folder1
        |   `-- subfolder1
        |       `-- zipfile1.zip
        `-- folder2
            `-- image1.jpg
        """
        # XXX this big hugre
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder1', 'FooFolder 1')
        factory.manage_addFolder('folder2', 'FooFolder 2')
        folder1 = self.root._getOb('folder1')
        folder2 = self.root._getOb('folder2')
        factory = folder1.manage_addProduct['Silva']
        factory.manage_addFolder('subfolder1', 'Sub FooFolder')
        subfolder1 = folder1._getOb('subfolder1')

        # By default, all used_space should be at 0
        self.assertEqual(self.root.used_space, 0)
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(subfolder1.used_space, 0)

        # Add a file
        factory = subfolder1.manage_addProduct['Silva']
        with self.layer.open_fixture('test2.zip') as source:
            factory.manage_addFile('file.zip', 'Zip File', source)
            zipfile_size = source.tell()
            zipfile = subfolder1._getOb('file.zip')

        self.assertTrue(verifyObject(IAsset, zipfile))
        self.assertEqual(zipfile.get_file_size(), zipfile_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zipfile_size)
        self.assertEqual(self.root.used_space, zipfile_size)

        # Change file data
        with self.layer.open_fixture('test1.zip') as source:
            zipfile.set_file(source)
            zipfile_size = source.tell()
        self.assertEqual(zipfile.get_file_size(), zipfile_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zipfile_size)
        self.assertEqual(self.root.used_space, zipfile_size)
        self.assertEqual(folder2.used_space, 0)

        # Add an image
        factory = folder2.manage_addProduct['Silva']
        with self.layer.open_fixture('torvald.jpg') as source:
            factory.manage_addImage('image1.jpg', 'Image File', source)
            image_size = source.tell()

        # Verify added image
        image = folder2._getOb('image1.jpg')
        self.assertTrue(verifyObject(IAsset, image))
        self.assertEqual(image.get_file_size(), image_size)
        # And check used space
        self.assertEqual(self.root.used_space, zipfile_size + image_size)
        self.assertEqual(folder2.used_space, image_size)
        # Change image and check size
        with self.layer.open_fixture('testimage.gif') as source:
            image.set_image(source)
            image_size = source.tell()
        # And check used space
        self.assertEqual(image.get_file_size(), image_size)
        self.assertEqual(subfolder1.used_space, zipfile_size)
        self.assertEqual(self.root.used_space, zipfile_size + image_size)
        self.assertEqual(folder2.used_space, image_size)

        # Try cut and paste
        manager2 = IContainerManager(folder2)
        with manager2.mover() as mover:
            mover(folder1['subfolder1'])

        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(self.root.used_space, zipfile_size + image_size)
        self.assertEqual(folder2.used_space, zipfile_size + image_size)

        # Try cut and ghost paste
        manager1 = IContainerManager(folder1)
        with manager1.ghoster() as ghoster:
            ghoster(folder2['subfolder1'])

        # And check used space. Ghost Assets don't use any quota.
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(self.root.used_space, zipfile_size + image_size)
        self.assertEqual(folder2.used_space, zipfile_size + image_size)

        # Delete the ghost
        with manager1.deleter() as deleter:
            deleter(folder1['subfolder1'])

        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(self.root.used_space, zipfile_size + image_size)
        self.assertEqual(folder2.used_space, zipfile_size + image_size)

        # Try copy and paste
        with manager1.copier() as copier:
            copier(folder2['image1.jpg'])

        # And check used space
        self.assertEqual(folder1.used_space, image_size)
        self.assertEqual(self.root.used_space, zipfile_size + (2 * image_size))
        self.assertEqual(folder2.used_space, zipfile_size + image_size)

        # Clean, and check each time
        manager = IContainerManager(self.root)
        with manager.deleter() as deleter:
            deleter(self.root['folder2'])
        self.assertEqual(self.root.used_space, image_size)
        with manager.deleter() as deleter:
            deleter(self.root['folder1'])
        self.assertEqual(self.root.used_space, 0)

    def test_zip_import(self):
        """Test the import of Zip file with quota system activated.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.assertEqual(self.root.used_space, 0)
        self.assertEqual(self.root.folder.used_space, 0)

        with self.layer.open_fixture('test1.zip') as source:
            IArchiveFileImporter(self.root.folder).importArchive(source)
        self.assertEqual(self.root.folder.used_space, 10950)
        self.assertEqual(self.root.used_space, 10950)

        with IContainerManager(self.root).deleter() as deleter:
            deleter(self.root.folder)
        self.assertEqual(self.root.used_space, 0)

    def test_xml_import(self):
        """Test the import of a XML file with quota system activited.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.assertEqual(self.root.used_space, 0)
        self.assertEqual(self.root.folder.used_space, 0)

        with self.layer.open_fixture('test_import_file.zip') as source:
            importer = ZipImporter(self.root.folder, TestRequest())
            importer.importStream(source)
        self.assertEqual(self.root.folder.used_space, 35512)
        self.assertEqual(self.root.used_space, 35512)

        with IContainerManager(self.root).deleter() as deleter:
            deleter(self.root.folder)
        self.assertEqual(self.root.used_space, 0)

    def test_add_file_over_quota(self):
        """ Test an exception is raised when adding a file will
        put the folder over quota
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.assertEqual(self.root.folder.used_space, 0)

        set_quota(self.root, 1) # 1M
        factory = self.root.folder.manage_addProduct['Silva']
        with self.layer.open_fixture('test3.zip') as source:
            factory.manage_addFile('zipfile1.zip', 'Zip File', source)
            source.seek(0)
            with self.assertRaises(OverQuotaException):
                factory.manage_addFile('zipfile2.zip', 'Zip File', source)

    def test_copy_paste_over_quota(self):
        """ Test an exception is raised when a copy is made.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.assertEqual(self.root.folder.used_space, 0)

        factory = self.root.folder.manage_addProduct['Silva']
        with self.layer.open_fixture('test3.zip') as source:
            factory.manage_addFile('zipfile1.zip', 'Zip File', source)
            source.seek(0)
            factory.manage_addFile('zipfile2.zip', 'Zip File', source)

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('pub', 'Publication')
        set_quota(self.root.pub, 1) # 1M

        with self.assertRaises(OverQuotaException):
            with IContainerManager(self.root.pub).copier() as copier:
                copier(self.root.folder)

    def test_cut_and_paste_do_not_raise_over_quota(self):
        """Test than moving to a folder would not exceed the quota.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.assertEqual(self.root.folder.used_space, 0)

        # Set a global quota of 4 MB.
        set_quota(self.root, 4)
        self.assertEqual(self.root.get_current_quota(), 4)
        factory = self.root.folder.manage_addProduct['Silva']
        with self.layer.open_fixture('test3.zip') as source:
            factory.manage_addFile('zipfile1.zip', 'Zip File', source)
            source.seek(0)
            factory.manage_addFile('zipfile2.zip', 'Zip File', source)

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')

        # Set the quota to 1 MB and move the folder (too small for this test).
        set_quota(self.root.publication, 1)
        self.assertEqual(self.root.publication.get_current_quota(), 1)
        factory = self.root.publication.manage_addProduct['Silva']
        with IContainerManager(self.root.publication).mover() as mover:
            with self.assertRaises(OverQuotaException):
                mover(self.root.folder)

        # Delete the quota on the publication (soo retrieve root quota)
        set_quota(self.root.publication, 0)
        self.assertEqual(self.root.publication.get_current_quota(), 4)
        with IContainerManager(self.root.publication).mover() as mover:
            mover(self.root.folder)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActivationQuotaTestCase))
    suite.addTest(unittest.makeSuite(QuotaTestCase))
    return suite
