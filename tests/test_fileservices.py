# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import component
from zope.interface import implements
from zope.interface.verify import verifyObject

import helpers
import SilvaTestCase

from Products.Silva import File
from Products.Silva import interfaces
from Products.Silva.Image import havePIL
from Products.Silva.File import FILESYSTEM_STORAGE_AVAILABLE


class FileServicesTest(SilvaTestCase.SilvaFileTestCase):

    implements(SilvaTestCase.ISilvaTestBlobs)

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

    def isZODBImage(self, image):
        self.isZODBFile(image.hires_image)

    def isZODBFile(self, file):
        self.failUnless(interfaces.IZODBFile.providedBy(file))

    def isBlobImage(self, image):
        self.isBlobFile(image.hires_image)

    def isBlobFile(self, file):
        self.failUnless(interfaces.IBlobFile.providedBy(file))

    def test_service(self):
        self.failUnless(verifyObject(interfaces.IFilesService,
                                     self.root.service_files))

        self.root.service_files.storage = File.ZODBFile
        file = self.root.service_files.newFile('test')
        self.isZODBFile(file)
        self.root.service_files.storage = File.BlobFile
        file = self.root.service_files.newFile('test')
        self.isBlobFile(file)

    def test_manage_convertStorage(self):
        # By default we use ZODB storage
        self.root.service_files.storage = File.ZODBFile

        self.add_test_image('testimage', self.root)
        self.add_test_image('testimage', self.root.folder1)
        self.add_test_image('testimage', self.root.folder1.folder1in1)
        self.add_test_file('testfile', self.root)
        self.add_test_file('testfile', self.root.folder1.folder1in1)

        self.isZODBImage(self.root.testimage)
        self.isZODBImage(self.root.folder1.testimage)
        self.isZODBImage(self.root.folder1.folder1in1.testimage)

        self.isZODBFile(self.root.testfile)
        self.isZODBFile(self.root.folder1.folder1in1.testfile)

        image_data = self.root.testimage.getImage(hires=1)
        file_data = self.root.testfile.get_content()
        form = component.getMultiAdapter((self.root.service_files, self.root.REQUEST),
                                         name='manage_filesservice')

        # Convert to Blobs
        self.root.service_files.storage = File.BlobFile
        form.convert()

        self.isBlobImage(self.root.testimage)
        self.isBlobImage(self.root.folder1.testimage)
        self.isZODBImage(self.root.folder1.folder1in1.testimage)

        self.isBlobFile(self.root.testfile)
        self.isZODBFile(self.root.folder1.folder1in1.testfile)

        converted_image_data = self.root.testimage.getImage(hires=1)
        self.assertEquals(image_data, converted_image_data)
        converted_file_data = self.root.testfile.get_content()
        self.assertEquals(file_data, converted_file_data)

        # Convert back to ZODB
        self.root.service_files.storage = File.ZODBFile
        form.convert()

        self.isZODBImage(self.root.testimage)
        self.isZODBImage(self.root.folder1.testimage)
        self.isZODBImage(self.root.folder1.folder1in1.testimage)

        self.isZODBFile(self.root.testfile)
        self.isZODBFile(self.root.folder1.folder1in1.testfile)

        converted_image_data = self.root.testimage.getImage(hires=1)
        self.assertEquals(image_data, converted_image_data)
        converted_file_data = self.root.testfile.get_content()
        self.assertEquals(file_data, converted_file_data)


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileServicesTest))
    return suite
