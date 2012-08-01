# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import unittest
from StringIO import StringIO
from zipfile import ZipFile

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Products.Silva.silvaxml import xmlimport
from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer, TestRequest
from silva.core.interfaces import IArchiveFileImporter, IAsset
from silva.core.interfaces import IContainerManager
from silva.core.services.interfaces import IExtensionService


def test_file_size(filename):
    """Return the size of a file.
    """
    with open_test_file(filename, mode='rb') as file_handle:
        file_handle.seek(0, 2)
        return file_handle.tell()


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
        service = getUtility(IExtensionService)
        self.assertEqual(service.get_quota_subsystem_status(), None)
        service.enable_quota_subsystem()
        self.assertEqual(service.get_quota_subsystem_status(), True)
        service.disable_quota_subsystem()
        self.assertEqual(service.get_quota_subsystem_status(), None)

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
        with open_test_file('test1.zip') as source_file:
            factory.manage_addFile('zipfile1.zip', 'Zip File', source_file)
        zip1_size = test_file_size('test1.zip')
        factory = folder2.manage_addProduct['Silva']
        with open_test_file('torvald.jpg') as source_file:
            factory.manage_addImage('image1.jpg', 'Image File', source_file)
        image1_size = test_file_size('torvald.jpg')

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
        self.layer.login('editor')
        self.root.service_extensions.enable_quota_subsystem()

    def test_validate_quota(self):
        """Test validate quota
        Content structure:

        root
        `-- pub1
            `-- folder1
                |-- pub2
                `-- pub3
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('pub1', 'Publication 1')
        pub1 = self.root.pub1
        factory = pub1.manage_addProduct['Silva']
        factory.manage_addFolder('folder1', 'Folder 1')
        folder1 = self.root.pub1.folder1
        factory = folder1.manage_addProduct['Silva']
        factory.manage_addPublication('pub2', 'Publication 2')
        factory.manage_addPublication('pub3', 'Publication 3')
        pub3 = self.root.pub1.folder1.pub3

        # By default, the quota is 0
        self.assertEqual(pub1.get_current_quota(), 0)
        self.assertEqual(pub3.get_current_quota(), 0)

        # Wanted quota check if the wanted value is correct
        self.assertFalse(pub1.validate_wanted_quota(-10))
        self.assertTrue(pub1.validate_wanted_quota(10))

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
        factory.manage_addFile(
            'zipfile1.zip', 'Zip File', open_test_file('test2.zip'))
        zip1 = subfolder1._getOb('zipfile1.zip')

        self.assertTrue(verifyObject(IAsset, zip1))
        zip2_size = test_file_size('test2.zip')
        self.assertEqual(zip1.get_file_size(), zip2_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip2_size)
        self.assertEqual(self.root.used_space, zip2_size)

        # Change file data
        zip1.set_file(open_test_file('test1.zip'))
        zip1_size = test_file_size('test1.zip')
        self.assertEqual(zip1.get_file_size(), zip1_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(self.root.used_space, zip1_size)
        self.assertEqual(folder2.used_space, 0)

        # Add an image
        factory = folder2.manage_addProduct['Silva']
        factory.manage_addImage(
            'image1.jpg', 'Image File', open_test_file('torvald.jpg'))
        image1 = folder2._getOb('image1.jpg')
        verifyObject(IAsset, image1)
        image2_size = test_file_size('torvald.jpg')
        self.assertEqual(image1.get_file_size(), image2_size)
        # And check used space
        self.assertEqual(self.root.used_space, zip1_size + image2_size)
        self.assertEqual(folder2.used_space, image2_size)
        # Change image and check size
        image1.set_image(open_test_file('testimage.gif'))
        image1_size = test_file_size('testimage.gif')
        self.assertEqual(image1.get_file_size(), image1_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(self.root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Try cut and paste
        manager2 = IContainerManager(folder2)
        with manager2.mover() as mover:
            mover(folder1['subfolder1'])

        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(self.root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Try cut and ghost paste
        manager1 = IContainerManager(folder1)
        with manager1.ghoster() as ghoster:
            ghoster(folder2['subfolder1'])

        # And check used space
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(self.root.used_space, (2 * zip1_size) + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Delete the ghost
        with manager1.deleter() as deleter:
            deleter(folder1['subfolder1'])

        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(self.root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Try copy and paste
        with manager1.copier() as copier:
            copier(folder2['image1.jpg'])

        # And check used space
        self.assertEqual(folder1.used_space, image1_size)
        self.assertEqual(self.root.used_space, zip1_size + (2 * image1_size))
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Clean, and check each time
        manager = IContainerManager(self.root)
        with manager.deleter() as deleter:
            deleter(self.root['folder2'])
        self.assertEqual(self.root.used_space, image1_size)
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

        with open_test_file('test1.zip') as source_file:
            IArchiveFileImporter(self.root.folder).importArchive(source_file)
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

        with open_test_file('test_import_file.zip') as source_file:
            source_zip = ZipFile(source_file)
            import_file = StringIO(source_zip.read('silva.xml'))
            xmlimport.importFromFile(
                import_file, self.root.folder, TestRequest(),
                zip_file=source_zip)
        self.assertEqual(self.root.folder.used_space, 35512)
        self.assertEqual(self.root.used_space, 35512)

        with IContainerManager(self.root).deleter() as deleter:
            deleter(self.root.folder)
        self.assertEqual(self.root.used_space, 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActivationQuotaTestCase))
    suite.addTest(unittest.makeSuite(QuotaTestCase))
    return suite
