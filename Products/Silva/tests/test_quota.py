# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import unittest

from zope.interface.verify import verifyObject

from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer
from silva.core import interfaces

def test_file_size(filename):
    """Return the size of a file.
    """
    with open_test_file(filename, mode='rb') as file_handle:
        file_handle.seek(0, 2)
        return file_handle.tell()


class QuotaTest(unittest.TestCase):
    """Test quota system implementation.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def _enable_quota(self):
        self.root.service_extensions.enable_quota_subsystem()

    def test_quota(self):
        """Test the quota system.
        Content structure:

        root
        `-- pub1
            `-- folder1
                `-- pub2
                    `--pub3
        """
        self._enable_quota()

        self.root.manage_addProduct['Silva'].manage_addPublication(
            'pub1', 'Publication 1')
        pub1 = self.root.pub1
        pub1.manage_addProduct['Silva'].manage_addFolder('folder1', 'Folder 1')
        folder1 = pub1.folder1
        folder1.manage_addProduct['Silva'].manage_addPublication(
            'pub2', 'Publication 2')
        pub2 = folder1.pub2
        folder1.manage_addProduct['Silva'].manage_addPublication(
            'pub3', 'Publication 3')
        pub3 = folder1.pub3

        # By default, the quota is 0
        self.assertEqual(pub1.get_current_quota(), 0)
        self.assertEqual(pub3.get_current_quota(), 0)

        # Wanted quota check if the wanted value is correct
        self.failIf(pub1.validate_wanted_quota(-10))
        self.failUnless(pub1.validate_wanted_quota(10))

        # FIXME: we can't test it like this. We have to make
        # functional tests (invalid request object in tests).

    def test_folder_action(self):
        """Test that folder action update used space.
        Content structure:

        root
        |-- folder1
        |   `-- subfolder
        |       `-- zipfile1.zip
        `-- folder2
            `-- image1.jpg
        """
        self._enable_quota()

        root = self.root
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder1', 'FooFolder 1')
        folder1 = getattr(root, 'folder1')
        factory.manage_addFolder('folder2', 'FooFolder 2')
        folder2 = getattr(root, 'folder2')
        factory = folder1.manage_addProduct['Silva']
        factory.manage_addFolder('subfolder1', 'Sub FooFolder')
        subfolder1 = getattr(folder1, 'subfolder1')

        # By default, all used_space should be at 0
        self.assertEqual(root.used_space, 0)
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(subfolder1.used_space, 0)

        # Add a file
        factory = subfolder1.manage_addProduct['Silva']
        factory.manage_addFile(
            'zipfile1.zip', 'Zip File', open_test_file('test2.zip'))
        zip1 = getattr(subfolder1, 'zipfile1.zip')

        verifyObject(interfaces.IAsset, zip1)
        zip2_size = test_file_size('test2.zip')
        self.assertEqual(zip1.get_file_size(), zip2_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip2_size)
        self.assertEqual(root.used_space, zip2_size)
        # Change file data
        zip1.set_file_data(open_test_file('test1.zip'))
        zip1_size = test_file_size('test1.zip')
        self.assertEqual(zip1.get_file_size(), zip1_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(root.used_space, zip1_size)
        self.assertEqual(folder2.used_space, 0)

        # Add an image
        factory = folder2.manage_addProduct['Silva']
        factory.manage_addImage(
            'image1.jpg', 'Image File', open_test_file('torvald.jpg'))
        image1 = getattr(folder2, 'image1.jpg')
        verifyObject(interfaces.IAsset, image1)
        image2_size = test_file_size('torvald.jpg')
        self.assertEqual(image1.get_file_size(), image2_size)
        # And check used space
        self.assertEqual(root.used_space, zip1_size + image2_size)
        self.assertEqual(folder2.used_space, image2_size)
        # Change image and check size
        image1.set_image(open_test_file('testimage.gif'))
        image1_size = test_file_size('testimage.gif')
        self.assertEqual(image1.get_file_size(), image1_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Try cut and paste
        folder1.action_cut(['subfolder1'], self.root.REQUEST)
        folder2.action_paste(self.root.REQUEST)

        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Try cut and ghost paste
        folder2.action_cut(['subfolder1'], self.root.REQUEST)
        folder1.action_paste_to_ghost(self.root.REQUEST)

        # And check used space
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(root.used_space, (2 * zip1_size) + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Delete the ghost
        folder1.action_delete(['subfolder1'])

        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Try copy and paste
        folder2.action_copy(['image1.jpg'], self.root.REQUEST)
        folder1.action_paste(self.root.REQUEST)

        # And check used space
        self.assertEqual(folder1.used_space, image1_size)
        self.assertEqual(root.used_space, zip1_size + (2 * image1_size))
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Clean, and check each time
        root.action_delete(['folder2'])
        self.assertEqual(root.used_space, image1_size)
        root.action_delete(['folder1'])
        self.assertEqual(root.used_space, 0)

    def test_zip_import(self):
        """Test the import of Zip file with quota system activited.
        """
        self._enable_quota()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        importer = interfaces.IArchiveFileImporter(self.root.folder)
        importer.importArchive(open_test_file('test1.zip'))

        self.assertNotEqual(self.root.used_space, 0)

        self.root.manage_delObjects(['folder'])
        self.assertEqual(self.root.used_space, 0)

    def test_zip_import2(self):
        """Test the import of Zip file with quota system activited.
        """
        self._enable_quota()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

        importer = interfaces.IArchiveFileImporter(self.root.folder)
        importer.importArchive(open_test_file('test2.zip'))

        self.assertNotEqual(self.root.used_space, 0)

        self.root.manage_delObjects(['folder'])
        self.assertEqual(self.root.used_space, 0)

    def test_extension(self):
        """Test that we can disable the extension.  After, create some
        content (same structure than the test folderAction), activate
        it, and check that all values are updated.
        """
        root = self.root
        s_ext = root.service_extensions
        self.assertEqual(s_ext.get_quota_subsystem_status(), False,
                         "Quota should be disable by default")
        s_ext.enable_quota_subsystem()
        self.assertEqual(s_ext.get_quota_subsystem_status(), True)
        s_ext.disable_quota_subsystem()
        self.assertEqual(s_ext.get_quota_subsystem_status(), False)

        # Create some content
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder1', 'FooFolder 1')
        folder1 = getattr(root, 'folder1')
        factory.manage_addFolder('folder2', 'FooFolder 2')
        folder2 = getattr(root, 'folder2')
        factory = folder1.manage_addProduct['Silva']
        factory.manage_addFolder('subfolder', 'Sub FooFolder')
        subfolder1 = getattr(folder1, 'subfolder')
        factory = subfolder1.manage_addProduct['Silva']
        factory.manage_addFile(
            'zipfile1.zip', 'Zip File', open_test_file('test1.zip'))
        zip1 = getattr(subfolder1, 'zipfile1.zip')
        zip1_size = test_file_size('test1.zip')
        factory = folder2.manage_addProduct['Silva']
        factory.manage_addImage(
            'image1.jpg', 'Image File', open_test_file('torvald.jpg'))
        image1 = getattr(folder2, 'image1.jpg')
        image1_size = test_file_size('torvald.jpg')

        # No counting should be done (extensions not activated, and
        # site empty)
        self.assertEqual(root.used_space, 0)
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(folder2.used_space, 0)

        # Activate it again
        s_ext.enable_quota_subsystem()

        # Values should be updated
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Disable
        s_ext.disable_quota_subsystem()

        # Do some changes
        folder1.action_delete(['subfolder'])
        root.action_copy(['folder2'], self.root.REQUEST)
        folder1.action_paste(self.root.REQUEST)

        # Nothing had change
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Re-enable
        s_ext.enable_quota_subsystem()
        # Values should be updated
        self.assertEqual(root.used_space, (2 * image1_size))
        self.assertEqual(folder1.used_space, image1_size)
        self.assertEqual(folder2.used_space, image1_size)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuotaTest))
    return suite
