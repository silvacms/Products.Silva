# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import transaction

from silva.core import interfaces
from silva.core.services.interfaces import IFilesService
from zope import component
from zope.interface.verify import verifyObject

from zExceptions import BadRequest

from Products.Silva import File
from Products.Silva.tests import helpers
from Products.Silva.testing import FunctionalLayer, TestCase


class FileServicesTest(TestCase):
    """Test file services features.
    """
    layer = FunctionalLayer

    def setUp(self):
        """Test content structure:

        root/service_files (by default)
        root/folder1
        root/folder1/folder1in1
        root/folder1/folder1in1/folder1in1in1
        root/folder1/folder1in1/folder1in1in1/service_files
        root/folder2
        """
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder1', 'Folder 1')
        factory.manage_addFolder('folder2', 'Folder 2')

        factory = self.root.folder1.manage_addProduct['Silva']
        factory.manage_addPublication('folder1in1', 'Folder 1 in 1')

        factory = self.root.folder1.folder1in1.manage_addProduct['Silva']
        factory.manage_addFolder('folder1in1in1', 'Folder 1 in 1 in 1')

        # We can only add a new service in a site
        interfaces.ISiteManager(self.root.folder1.folder1in1).make_site()
        factory.manage_addFilesService()

    def add_test_file(self, id, context):
        file_handle = helpers.openTestFile('photo.tif')
        context.manage_addProduct['Silva'].manage_addFile(
            id, 'Test File', file_handle)
        file_handle.close()

    def add_test_image(self, id, context):
        file_handle = helpers.openTestFile('photo.tif')
        context.manage_addProduct['Silva'].manage_addImage(
            id, 'Test Image', file_handle)
        file_handle.close()

    def isZODBImage(self, image):
        self.isZODBFile(image.hires_image)

    def isZODBFile(self, file):
        self.assertTrue(interfaces.IZODBFile.providedBy(file))

    def isBlobImage(self, image):
        self.isBlobFile(image.hires_image)

    def isBlobFile(self, file):
        self.assertTrue(interfaces.IBlobFile.providedBy(file))

    def test_service(self):
        service = component.getUtility(IFilesService)
        self.assertEquals(self.root.service_files, service)
        self.assertTrue(
            verifyObject(IFilesService, service))

        service.storage = File.ZODBFile
        zodb_file = service.new_file('test')
        self.isZODBFile(zodb_file)
        self.assertEqual(
            service.is_file_using_correct_storage(zodb_file), True)

        service.storage = File.BlobFile
        blob_file = service.new_file('test')
        self.isBlobFile(blob_file)
        self.assertEqual(
            service.is_file_using_correct_storage(zodb_file), False)
        self.assertEqual(
            service.is_file_using_correct_storage(blob_file), True)

        factory = self.root.folder1.manage_addProduct['Silva']
        self.assertRaises(
            BadRequest, factory.manage_addFilesService, 'service_files')

    def test_manage_convert_storage(self):
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

        image_data = self.root.testimage.get_image(hires=1)
        file_data = self.root.testfile.get_file()
        form = component.getMultiAdapter(
            (self.root.service_files, self.root.REQUEST),
            name='manage_settings').allSubforms[1]

        transaction.commit()
        # Convert to Blobs
        self.root.service_files.storage = File.BlobFile
        form.convert()

        self.isBlobImage(self.root.testimage)
        self.isBlobImage(self.root.folder1.testimage)
        self.isZODBImage(self.root.folder1.folder1in1.testimage)

        self.isBlobFile(self.root.testfile)
        self.isZODBFile(self.root.folder1.folder1in1.testfile)

        converted_image_data = self.root.testimage.get_image(hires=1)
        self.assertEquals(image_data, converted_image_data)
        converted_file_data = self.root.testfile.get_file()
        self.assertEquals(file_data, converted_file_data)

        # Convert back to ZODB
        self.root.service_files.storage = File.ZODBFile
        form.convert()

        self.isZODBImage(self.root.testimage)
        self.isZODBImage(self.root.folder1.testimage)
        self.isZODBImage(self.root.folder1.folder1in1.testimage)

        self.isZODBFile(self.root.testfile)
        self.isZODBFile(self.root.folder1.folder1in1.testfile)

        converted_image_data = self.root.testimage.get_image(hires=1)
        self.assertHashEqual(image_data, converted_image_data)
        converted_file_data = self.root.testfile.get_file()
        self.assertHashEqual(file_data, converted_file_data)

    def test_convert_keep_metadata(self):
        assert False, 'TBD'

    def test_convert_keep_markers(self):
        assert False, 'TBD'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileServicesTest))
    return suite
