# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
import transaction

from silva.core.interfaces import ISiteManager
from silva.core.interfaces import IImage, IZODBFile, IBlobFile
from silva.core.services.interfaces import IFilesService
from silva.core.views.interfaces import ICustomizableTag
from zope.interface import alsoProvides
from zope.component import getUtility
from zope.interface.verify import verifyObject

from zExceptions import BadRequest

from Products.Silva import File
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer, TestCase


class ITestTag(ICustomizableTag):
    """Test tag.
    """


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
        ISiteManager(self.root.folder1.folder1in1).make_site()
        factory.manage_addFilesService()

    def assertIsZODBImage(self, content):
        self.assertTrue(IImage.providedBy(content))
        self.assertTrue(IZODBFile.providedBy(content.hires_image))

    def assertIsZODBFile(self, content):
        self.assertTrue(IZODBFile.providedBy(content))

    def assertIsBlobImage(self, content):
        self.assertTrue(IImage.providedBy(content))
        self.assertTrue(IBlobFile.providedBy(content.hires_image))

    def assertIsBlobFile(self, content):
        self.assertTrue(IBlobFile.providedBy(content))

    def addTestFile(self, id, context):
        with open_test_file('photo.tif') as file_handle:
            factory = context.manage_addProduct['Silva']
            factory.manage_addFile(id, 'Test File', file_handle)

    def addTestImage(self, id, context):
        with open_test_file('photo.tif') as file_handle:
            factory = context.manage_addProduct['Silva']
            factory.manage_addImage(id, 'Test Image', file_handle)

    def test_service(self):
        """Test service implementation.
        """
        service = getUtility(IFilesService)
        self.assertEquals(self.root.service_files, service)
        self.assertTrue(verifyObject(IFilesService, service))

        service.storage = File.ZODBFile
        zodb_file = service.new_file('test')
        self.assertIsZODBFile(zodb_file)
        self.assertTrue(service.is_file_using_correct_storage(zodb_file))

        service.storage = File.BlobFile
        blob_file = service.new_file('test')
        self.assertIsBlobFile(blob_file)
        self.assertFalse(service.is_file_using_correct_storage(zodb_file))
        self.assertTrue(service.is_file_using_correct_storage(blob_file))

        # You can only add a service file in a local site.
        factory = self.root.folder1.manage_addProduct['Silva']
        with self.assertRaises(BadRequest):
            factory.manage_addFilesService('service_files')

    def test_manage_convert_storage(self):
        """Test service convert.
        """
        # By default we use ZODB storage
        service = getUtility(IFilesService)
        service.storage = File.ZODBFile

        self.addTestImage('testimage', self.root)
        self.addTestImage('testimage', self.root.folder1)
        self.addTestImage('testimage', self.root.folder1.folder1in1)
        self.addTestFile('testfile', self.root)
        self.addTestFile('testfile', self.root.folder1.folder1in1)

        self.assertIsZODBImage(self.root.testimage)
        self.assertIsZODBImage(self.root.folder1.testimage)
        self.assertIsZODBImage(self.root.folder1.folder1in1.testimage)

        self.assertIsZODBFile(self.root.testfile)
        self.assertIsZODBFile(self.root.folder1.folder1in1.testfile)

        image_data = self.root.testimage.get_image(hires=1)
        file_data = self.root.testfile.get_file()

        transaction.commit()

        # Convert to Blobs
        service.storage = File.BlobFile
        service.convert_storage(self.root)

        self.assertIsBlobImage(self.root.testimage)
        self.assertIsBlobImage(self.root.folder1.testimage)
        self.assertIsZODBImage(self.root.folder1.folder1in1.testimage)

        self.assertIsBlobFile(self.root.testfile)
        self.assertIsZODBFile(self.root.folder1.folder1in1.testfile)

        self.assertHashEqual(
            image_data,
            self.root.testimage.get_image(hires=1))
        self.assertHashEqual(
            file_data,
            self.root.testfile.get_file())

        # Convert back to ZODB
        service.storage = File.ZODBFile
        service.convert_storage(self.root)

        self.assertIsZODBImage(self.root.testimage)
        self.assertIsZODBImage(self.root.folder1.testimage)
        self.assertIsZODBImage(self.root.folder1.folder1in1.testimage)

        self.assertIsZODBFile(self.root.testfile)
        self.assertIsZODBFile(self.root.folder1.folder1in1.testfile)

        self.assertHashEqual(
            image_data,
            self.root.testimage.get_image(hires=1))
        self.assertHashEqual(
            file_data,
            self.root.testfile.get_file())

    def test_convert_keep_metadata(self):
        """Test that converting the file storage keeps the metadata.
        """
        service = getUtility(IFilesService)
        service.storage = File.ZODBFile

        self.addTestImage('image', self.root)
        self.addTestFile('data', self.root)

        metadata = getUtility(IMetadataService).getMetadata(self.root.image)
        metadata.setValues('silva-content', {'maintitle': 'Image title'})
        metadata.setValues('silva-extra', {'comment': 'This is an image'})

        metadata = getUtility(IMetadataService).getMetadata(self.root.data)
        metadata.setValues('silva-content', {'maintitle': 'File title'})
        metadata.setValues('silva-extra', {'comment': 'This is a data file'})

        self.assertIsZODBImage(self.root.image)
        self.assertIsZODBFile(self.root.data)

        transaction.commit()

        # Convert to Blobs
        service.storage = File.BlobFile
        service.convert_storage(self.root)

        self.assertIsBlobImage(self.root.image)
        metadata = getUtility(IMetadataService).getMetadata(self.root.image)
        self.assertEqual(
            metadata.get('silva-content', 'maintitle'),
            'Image title')
        self.assertEqual(
            metadata.get('silva-extra', 'comment'),
            'This is an image')

        self.assertIsBlobFile(self.root.data)
        metadata = getUtility(IMetadataService).getMetadata(self.root.data)
        self.assertEqual(
            metadata.get('silva-content', 'maintitle'),
            'File title')
        self.assertEqual(
            metadata.get('silva-extra', 'comment'),
            'This is a data file')

    def test_convert_keep_markers(self):
        """Customization markers should be keept.
        """
        service = getUtility(IFilesService)
        service.storage = File.ZODBFile

        self.addTestImage('image', self.root)
        self.addTestFile('data', self.root)

        alsoProvides(self.root.image, ITestTag)
        alsoProvides(self.root.data, ITestTag)

        self.assertIsZODBImage(self.root.image)
        self.assertIsZODBFile(self.root.data)

        transaction.commit()

        # Convert to Blobs
        service.storage = File.BlobFile
        service.convert_storage(self.root)

        self.assertIsBlobImage(self.root.image)
        self.assertTrue(ITestTag.providedBy(self.root.image))
        self.assertIsBlobFile(self.root.data)
        self.assertTrue(ITestTag.providedBy(self.root.data))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileServicesTest))
    return suite
