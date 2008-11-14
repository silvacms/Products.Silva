# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface.verify import verifyObject

import helpers
import SilvaTestCase

from Products.Silva import interfaces
from Products.Silva.Image import havePIL
from Products.Silva.File import FILESYSTEM_STORAGE_AVAILABLE

# NOTE: these tests should all pass regardless of the availability of ExtFile

class FileServicesTest(SilvaTestCase.SilvaFileTestCase):

    def afterSetUp(self):
        """
        Test content structure:

        root/service_files (by default)
        root/folder1
        root/folder1/folder1in1
        root/folder1/folder1in1/folder1in1in1
        root/folder1/folder1in1/folder1in1in1/service_files
        root/folder2
        """
        root = self.root = self.getRoot()
        folder1 = self.add_folder(root, 'folder1', 'Folder 1')
        folder2 = self.add_folder(root, 'folder2', 'Folder 2')
        folder1in1 = self.add_folder(folder1, 'folder1in1', 'Folder 1 in 1')
        folder1in1in1 = self.add_folder(folder1in1, 'folder1in1in1', 'Folder 1 in 1 in 1')
        folder1in1.manage_addProduct['Silva'].manage_addFilesService(
            'service_files', 'Other Files Service')

    def add_test_file(self, id, context):
        file_handle = helpers.openTestFile('photo.tif')
        context.manage_addProduct['Silva'].manage_addFile(
            id, 'Test File', file_handle)
        file_handle.close()

    def add_test_image(self, id, context):
        if havePIL:
            file_handle = helpers.openTestFile('photo.tif')
        else:
            file_handle = helpers.openTestFile('silva.png')
        context.manage_addProduct['Silva'].manage_addImage(
            id, 'Test Image', file_handle)
        file_handle.close()

    def test_service(self):
        self.failUnless(verifyObject(interfaces.IFilesService, self.root.service_files))

    def test_manage_convertStorage(self):
        # by default we use ZODB storage
        self.add_test_image('testimage', self.root)
        self.add_test_image('testimage', self.root.folder1)
        self.add_test_image('testimage', self.root.folder1.folder1in1)
        self.add_test_image('testimage', self.root.folder2)
        self.add_test_file('testfile', self.root)
        self.add_test_file('testfile', self.root.folder1.folder1in1)
        self.assertEqual(self.root.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder1.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder1.folder1in1.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder2.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.folder2.testimage.image.meta_type, 'Image')
        self.assertEqual(
            self.root.testfile._file.meta_type, 'File')
        self.assertEqual(
            self.root.folder1.folder1in1.testfile._file.meta_type, 'File')
        if FILESYSTEM_STORAGE_AVAILABLE:
            self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 1)
            self.root.folder1.folder1in1.service_files.manage_convertStorage()
            self.assertEqual(
                self.root.folder1.folder1in1.testimage.image.meta_type, 'ExtImage')
            self.assertEqual(
                self.root.folder1.folder1in1.testfile._file.meta_type, 'ExtFile')
            self.root.folder1.folder1in1.service_files.manage_filesServiceEdit('', 0)
            self.root.folder1.folder1in1.service_files.manage_convertStorage()
            self.assertEqual(
                self.root.folder1.folder1in1.testimage.image.meta_type, 'Image')
            self.assertEqual(
                self.root.folder1.folder1in1.testfile._file.meta_type, 'File')

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileServicesTest))
    return suite
