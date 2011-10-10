# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
import unittest

from zope.interface.verify import verifyObject

from Products.Silva import File
from Products.Silva.helpers import create_new_filename
from Products.Silva.testing import (
    FunctionalLayer, TestCase, http, get_event_names)
from Products.Silva.tests import helpers
from silva.core import interfaces


class DefaultFileImplementationTestCase(TestCase):
    """Test default file implementation.
    """
    layer = FunctionalLayer
    implementation = None

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def create_test_file(self, filename='photo.tif'):
        file_handle = helpers.open_test_file(filename)
        self.file_data = file_handle.read()
        self.file_size = file_handle.tell()
        file_handle.seek(0)
        if self.implementation is not None:
            self.root.service_files.storage = self.implementation
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile(filename, 'Test File', file_handle)
        file_handle.close()
        return self.root._getOb(filename)

    def test_event(self):
        """Test that events are triggered.
        """
        self.create_test_file() # XXX Something more is created there 
        get_event_names()

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('file', 'Eventfull File')
        self.assertEquals(
            get_event_names(),
            ['ObjectWillBeAddedEvent', 'ObjectAddedEvent',
             'IntIdAddedEvent', 'ContainerModifiedEvent',
             'ObjectCreatedEvent'])

        self.root.file.set_file_data(StringIO("Some text file"))
        self.assertEquals(
            get_event_names(),
            ['ObjectModifiedEvent'])

        self.root.file.set_text_file_data("Text to set as file content")
        self.assertEquals(
            get_event_names(),
            ['ObjectModifiedEvent'])

    def test_content_image(self):
        """Test base content methods on a file that contains an image.
        """
        content = self.create_test_file()
        self.failUnless(verifyObject(interfaces.IAsset, content))
        self.failUnless(verifyObject(interfaces.IFile, content))

        self.assertEquals(content.content_type(), 'image/tiff')
        self.assertEquals(content.content_encoding(), None)
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'photo.tiff')
        self.assertEquals(content.get_mime_type(), 'image/tiff')
        self.assertHashEqual(content.get_content(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)
        # You cannot edit images as text
        self.assertEquals(content.can_edit_text(), False)

        # If you change the filename, you will get the new value afterward
        content.set_filename('image.tiff')
        self.assertEquals(content.get_filename(), 'image.tiff')

    def test_content_text(self):
        """Test base content methods on a file that contains text.
        """
        content = self.create_test_file('test_file_text.txt')
        self.failUnless(verifyObject(interfaces.IAsset, content))
        self.failUnless(verifyObject(interfaces.IFile, content))

        self.assertEquals(content.content_type(), 'text/plain; charset=utf-8')
        self.assertEquals(content.content_encoding(), None)
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'test_file_text.txt')
        self.assertEquals(content.get_mime_type(), 'text/plain')
        self.assertHashEqual(content.get_content(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)
        # You can edit text
        self.assertEquals(content.can_edit_text(), True)

        # If you change the filename, you will get the new value afterward
        content.set_filename('text.txt')
        self.assertEquals(content.get_filename(), 'text.txt')

    def test_content_compressed_text(self):
        """Test base content methods on a file that contains
        compressed text.
        """
        content = self.create_test_file('test_file_text.txt.gz')
        self.failUnless(verifyObject(interfaces.IAsset, content))
        self.failUnless(verifyObject(interfaces.IFile, content))

        self.assertEquals(content.content_type(), 'text/plain; charset=utf-8')
        self.assertEquals(content.content_encoding(), 'gzip')
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'test_file_text.txt.gz')
        self.assertEquals(content.get_mime_type(), 'text/plain')
        self.assertHashEqual(content.get_content(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)
        # You cannot edit compressed files
        self.assertEquals(content.can_edit_text(), False)

    def test_content_xml(self):
        """Test base content methods on a file that contains xml.
        """
        content = self.create_test_file('test_document.xml')
        self.failUnless(verifyObject(interfaces.IAsset, content))
        self.failUnless(verifyObject(interfaces.IFile, content))

        self.assertEquals(content.content_type(), 'text/xml')
        self.assertEquals(content.content_encoding(), None)
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'test_document.xml')
        self.assertEquals(content.get_mime_type(), 'text/xml')
        self.assertHashEqual(content.get_content(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)
        # You can edit text
        self.assertEquals(content.can_edit_text(), True)

    def test_download(self):
        """Test downloading file.
        """
        self.create_test_file()
        response = http('GET /root/photo.tif HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        downloaded_data = response.getBody()
        self.assertEquals(len(downloaded_data), self.file_size)
        self.assertHashEqual(downloaded_data, self.file_data)
        self.assertEquals(int(headers['Content-Length']), self.file_size)
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Disposition'],
                          'inline;filename=photo.tiff')
        self.failUnless('Last-Modified' in headers)

    def test_not_modified(self):
        """Test downloading a file if it as been modified after a date.
        """
        self.create_test_file()
        response = http(
            'GET /root/photo.tif HTTP/1.1',
            parsed=True,
            headers={'If-Modified-Since': 'Sat, 29 Oct 2094 19:43:31 GMT'})
        self.assertEquals(response.getStatus(), 304)
        self.assertEquals(len(response.getBody()), 0)

    def test_head_request(self):
        """Test HEAD requests on Files.
        """
        self.create_test_file()
        response = http('HEAD /root/photo.tif HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        # Even on HEAD requests where there is no body, Content-Lenght
        # should be the size of the file.
        self.assertEquals(int(headers['Content-Length']), self.file_size)
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Disposition'],
                          'inline;filename=photo.tiff')
        self.failUnless('Last-Modified' in headers)
        self.assertEquals(len(response.getBody()), 0)

    def test_asset_data(self):
        """Test asset data adapter implementation.
        """
        content = self.create_test_file()
        assetdata = interfaces.IAssetData(content)
        self.failUnless(verifyObject(interfaces.IAssetData, assetdata))
        self.assertHashEqual(self.file_data, assetdata.getData())

    def test_rename_filename(self):
        """If you rename the file, the filename gets updated, and
        replace any existing wrong extension.
        """
        self.create_test_file()
        self.root.manage_renameObject('photo.tif', 'renamedfile')
        testfile = self.root['renamedfile']
        self.assertEqual(testfile.get_filename(), 'renamedfile.tiff')

        self.root.manage_renameObject('renamedfile', 'customfile.pdf')
        testfile = self.root['customfile.pdf']
        self.assertEqual(testfile.get_filename(), 'customfile.tiff')


class BlobFileImplementationTestCase(DefaultFileImplementationTestCase):
    """Test blob file implementation.
    """
    implementation = File.BlobFile


class ZODBFileImplementationTestCase(DefaultFileImplementationTestCase):
    """Test ZODB file implementation.
    """
    implementation = File.ZODBFile


class FFSFileImplementationTestCase(DefaultFileImplementationTestCase):
    """Test file system file implementation.
    """
    implementation = File.FileSystemFile


class CreateNewFilenameTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def create_test_file(self, filename):
        with helpers.open_test_file(filename) as file_handle:
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFile('testfile', 'Test File', file_handle)
            return self.root.testfile

    def test_image_png_filename(self):
        testfile = self.create_test_file('photo.tif')

        create_new_filename(testfile, 'image')
        self.assertEqual(testfile.get_filename(), 'image.tiff')

    def test_image_png_filename_with_extension(self):
        testfile = self.create_test_file('photo.tif')

        create_new_filename(testfile, 'image.jpg')
        self.assertEqual(testfile.get_filename(), 'image.tiff')

    def test_tar_gz_filename(self):
        testfile = self.create_test_file('images.tar.gz')

        create_new_filename(testfile, 'files')
        self.assertEqual(testfile.get_filename(), 'files.gz')

    def test_tar_gz_filename_with_partial_extension(self):
        testfile = self.create_test_file('images.tar.gz')

        create_new_filename(testfile, 'files.tar')
        self.assertEqual(testfile.get_filename(), 'files.tar.gz')

    def test_tar_gz_filename_with_extension(self):
        testfile = self.create_test_file('images.tar.gz')

        create_new_filename(testfile, 'files.tar.gz')
        self.assertEqual(testfile.get_filename(), 'files.tar.gz')

    def test_zip_filename(self):
        testfile = self.create_test_file('test1.zip')

        create_new_filename(testfile, 'files')
        self.assertEqual(testfile.get_filename(), 'files.zip')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CreateNewFilenameTestCase))
    suite.addTest(unittest.makeSuite(DefaultFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(BlobFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(ZODBFileImplementationTestCase))
    if File.FILESYSTEM_STORAGE_AVAILABLE:
        suite.addTest(unittest.makeSuite(FFSFileImplementationTestCase))
    return suite
