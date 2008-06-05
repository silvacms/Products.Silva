# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface.verify import verifyObject

import SilvaTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import utils

from StringIO import StringIO

from Products.Silva.tests.test_archivefileimport import ArchiveFileImport
from Products.Silva.interfaces import IAsset

import os.path

data_directory = os.path.join(os.path.dirname(__file__), 'data')
zipfile1 = os.path.join(data_directory, 'test1.zip')
zipfile2 = os.path.join(data_directory, 'test2.zip')
imagefile1 = os.path.join(data_directory, 'torvald.jpg')
imagefile2 = os.path.join(data_directory, 'testimage.gif')

def fileSize(filename):
    """Return the size of a file.
    """
    fd = open(filename, 'r')
    fd.seek(0, 2)
    return fd.tell()


class QuotaTest(SilvaTestCase.SilvaTestCase, ArchiveFileImport):
    """Test quota system implementation.
    """

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

        root = self.root
        pub1 = self.add_publication(root, 'pub1', 'Publication 1')
        folder1 = self.add_folder(pub1, 'folder1', 'Folder 1')
        pub2 = self.add_publication(folder1, 'pub2', 'Publication 2')
        pub3 = self.add_publication(folder1, 'pub3', 'Publication 3')
        
        # By default, the quota is 0
        self.assertEqual(pub1.get_current_quota(), 0)
        self.assertEqual(pub3.get_current_quota(), 0)

        # Wanted quota check if the wanted value is correct
        self.failIf(pub1.validate_wanted_quota(-10))
        self.failUnless(pub1.validate_wanted_quota(10))

        # FIXME: we can't test it like this. We have to make
        # functional tests (invalid request object in tests).

    def test_folderAction(self):
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
        folder1 = self.add_folder(root, 'folder1', 'FooFolder 1')
        folder2 = self.add_folder(root, 'folder2', 'FooFolder 2')
        subfolder1 = self.add_folder(folder1, 'subfolder', 'Sub FooFolder')

        # By default, all used_space should be at 0
        self.assertEqual(root.used_space, 0)
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(subfolder1.used_space, 0)

        # Add a file
        zip1 = self.add_file(subfolder1, 'zipfile1.zip', 'Zip File', 
                             file=open(zipfile2))
        #verifyObject(IAsset, zip1)
        zip2_size = fileSize(zipfile2)
        self.assertEqual(zip1.get_file_size(), zip2_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip2_size)
        self.assertEqual(root.used_space, zip2_size)
        # Change file data
        zip1.set_file_data(open(zipfile1))
        zip1_size = fileSize(zipfile1)
        self.assertEqual(zip1.get_file_size(), zip1_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(root.used_space, zip1_size)
        self.assertEqual(folder2.used_space, 0)

        # Add an image
        image1 = self.add_image(folder2, 'image1.jpg', 'Image File', 
                                file=open(imagefile2))
        #verifyObject(IAsset, image1)
        image2_size = fileSize(imagefile2)
        self.assertEqual(image1.get_file_size(), image2_size)
        # And check used space
        self.assertEqual(root.used_space, zip1_size + image2_size)
        self.assertEqual(folder2.used_space, image2_size)
        # Change image and check size
        image1.set_image(open(imagefile1))
        image1_size = fileSize(imagefile1)
        self.assertEqual(image1.get_file_size(), image1_size)
        # And check used space
        self.assertEqual(subfolder1.used_space, zip1_size)
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, image1_size)

        # Try cut and paste
        folder1.action_cut(['subfolder'], self.app.REQUEST)
        folder2.action_paste(self.app.REQUEST)
        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Try cut and ghost paste
        folder2.action_cut(['subfolder'], self.app.REQUEST)
        folder1.action_paste_to_ghost(self.app.REQUEST)
        # And check used space
        self.assertEqual(folder1.used_space, zip1_size)
        self.assertEqual(root.used_space, (2 * zip1_size) + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Delete the ghost
        folder1.action_delete(['subfolder'])
        # And check used space
        self.assertEqual(folder1.used_space, 0)
        self.assertEqual(root.used_space, zip1_size + image1_size)
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Try copy and paste
        folder2.action_copy(['image1.jpg'], self.app.REQUEST)
        folder1.action_paste(self.app.REQUEST)
        # And check used space
        self.assertEqual(folder1.used_space, image1_size)
        self.assertEqual(root.used_space, zip1_size + (2 * image1_size))
        self.assertEqual(folder2.used_space, zip1_size + image1_size)

        # Clean, and check each time
        root.action_delete(['folder2'])
        self.assertEqual(root.used_space, image1_size)
        root.action_delete(['folder1'])
        self.assertEqual(root.used_space, 0)


    def test_zipImport(self):
        """Test the import of Zip file with quota system activited.
        """
        self._enable_quota()
        self.importArchiveFileDefaultSettingsNoSubdirsInArchive()
        self.assertNotEqual(self.root.used_space, 0)


    def test_zipOtherImport(self):
        """Test the import of Zip file with quota system activited.
        """
        self._enable_quota()
        self.importArchiveFileDefaultSettings()
        self.assertNotEqual(self.root.used_space, 0)


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
        folder1 = self.add_folder(root, 'folder1', 'FooFolder 1')
        folder2 = self.add_folder(root, 'folder2', 'FooFolder 2')
        subfolder1 = self.add_folder(folder1, 'subfolder', 'Sub FooFolder')
        zip1 = self.add_file(subfolder1, 'zipfile1.zip', 'Zip File', 
                             file=open(zipfile1))
        zip1_size = fileSize(zipfile1)
        image1 = self.add_image(folder2, 'image1.jpg', 'Image File', 
                                file=open(imagefile1))
        image1_size = fileSize(imagefile1)

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
        root.action_copy(['folder2'], self.app.REQUEST)
        folder1.action_paste(self.app.REQUEST)
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


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuotaTest))
    return suite
