# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

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
        root/folder
        root/folder/publication
        root/folder/publication/folder1in1in1
        root/folder/publication/service_files
        root/folder2
        """
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addFolder('contact', 'Contact Folder')

        factory = self.root.folder.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')

        factory = self.root.folder.publication.manage_addProduct['Silva']
        factory.manage_addFolder('folder1in1in1', 'Folder 1 in 1 in 1')

        # We can only add a new service in a site
        ISiteManager(self.root.folder.publication).make_site()
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

    def addTestFile(self, identifier, context):
        with self.layer.open_fixture('docs_export_2008-06-11.odt') as stream:
            factory = context.manage_addProduct['Silva']
            factory.manage_addFile(identifier, 'Test File', stream)

    def addTestImage(self, identifier, context):
        with self.layer.open_fixture('photo.tif') as stream:
            factory = context.manage_addProduct['Silva']
            factory.manage_addImage(identifier, 'Test Image', stream)

    def test_service(self):
        """Test service implementation.
        """
        service = getUtility(IFilesService)
        self.assertEquals(self.root.service_files, service)
        self.assertTrue(verifyObject(IFilesService, service))

        service.storage = File.ZODBFile
        zodb_file = service.new_file('test')
        self.assertTrue(IZODBFile.providedBy(zodb_file))
        self.assertTrue(service.is_file_using_correct_storage(zodb_file))

        service.storage = File.BlobFile
        blob_file = service.new_file('test')
        self.assertTrue(IBlobFile.providedBy(blob_file))
        self.assertFalse(IZODBFile.providedBy(blob_file))
        self.assertTrue(service.is_file_using_correct_storage(blob_file))
        self.assertFalse(service.is_file_using_correct_storage(zodb_file))

        # You can only add a service file in a local site.
        factory = self.root.folder.manage_addProduct['Silva']
        with self.assertRaises(BadRequest):
            factory.manage_addFilesService('service_files')

    def test_convert_zodb_to_blob(self):
        """Test converting from zodb storage to blob.
        """
        service = getUtility(IFilesService)
        service.storage = File.ZODBFile

        self.addTestImage('image', self.root)
        self.addTestImage('image', self.root.folder)
        self.addTestImage('image', self.root.folder.publication)
        self.addTestFile('file', self.root)
        self.addTestFile('file', self.root.folder.publication)

        self.assertIsZODBImage(self.root.image)
        self.assertEqual(self.root.image.get_filename(), 'image.tiff')
        self.assertEqual(self.root.image.get_content_type(), 'image/tiff')
        self.assertIsZODBImage(self.root.folder.image)
        self.assertIsZODBImage(self.root.folder.publication.image)

        self.assertIsZODBFile(self.root.file)
        self.assertEqual(self.root.file.get_filename(), 'file.odt')
        self.assertEqual(
            self.root.file.get_content_type(),
            'application/vnd.oasis.opendocument.text')
        self.assertEqual(self.root.file.get_content_encoding(), None)
        self.assertIsZODBFile(self.root.folder.publication.file)

        image_data = self.root.image.get_image(hires=1)
        file_data = self.root.file.get_file()

        transaction.commit()

        # Convert to blob storage.
        service.storage = File.BlobFile
        service.convert_storage(self.root)

        self.assertIsBlobImage(self.root.image)
        self.assertIsBlobImage(self.root.folder.image)
        self.assertIsZODBImage(self.root.folder.publication.image)
        self.assertIsBlobFile(self.root.file)
        self.assertIsZODBFile(self.root.folder.publication.file)

        # Data, filename, and content_type is preserved.
        self.assertEqual(self.root.image.get_filename(), 'image.tiff')
        self.assertEqual(self.root.image.get_content_type(), 'image/tiff')
        self.assertHashEqual(self.root.image.get_image(hires=1), image_data)
        self.assertEqual(self.root.file.get_filename(), 'file.odt')
        self.assertEqual(
            self.root.file.get_content_type(),
            'application/vnd.oasis.opendocument.text')
        self.assertEqual(self.root.file.get_content_encoding(), None)
        self.assertHashEqual(self.root.file.get_file(), file_data)

    def test_convert_blob_to_zodb(self):
        """Converting from blob to zodb is not supported, due to
        implementation limitation of OFS.Image. If you try to convert
        to zodb storage, nothing will happen.
        """
        service = getUtility(IFilesService)
        service.storage = File.BlobFile

        self.addTestImage('image', self.root)
        self.addTestImage('image', self.root.folder)
        self.addTestImage('image', self.root.folder.publication)
        self.addTestFile('file', self.root)
        self.addTestFile('file', self.root.folder.publication)

        self.assertIsBlobImage(self.root.image)
        self.assertEqual(self.root.image.get_filename(), 'image.tiff')
        self.assertEqual(self.root.image.get_content_type(), 'image/tiff')
        self.assertIsBlobImage(self.root.folder.image)
        self.assertIsBlobImage(self.root.folder.publication.image)

        self.assertIsBlobFile(self.root.file)
        self.assertEqual(self.root.file.get_filename(), 'file.odt')
        self.assertEqual(
            self.root.file.get_content_type(),
            'application/vnd.oasis.opendocument.text')
        self.assertIsBlobFile(self.root.folder.publication.file)

        transaction.commit()

        # Convert to blob storage.
        service.storage = File.ZODBFile
        service.convert_storage(self.root)

        self.assertIsBlobImage(self.root.image)
        self.assertEqual(self.root.image.get_filename(), 'image.tiff')
        self.assertEqual(self.root.image.get_content_type(), 'image/tiff')
        self.assertIsBlobImage(self.root.folder.image)
        self.assertIsBlobImage(self.root.folder.publication.image)

        self.assertIsBlobFile(self.root.file)
        self.assertEqual(self.root.file.get_filename(), 'file.odt')
        self.assertEqual(
            self.root.file.get_content_type(),
            'application/vnd.oasis.opendocument.text')
        self.assertIsBlobFile(self.root.folder.publication.file)

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
