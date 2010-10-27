# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
import unittest

from zope.interface.verify import verifyObject

from Products.Silva import File
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
        file_handle = helpers.openTestFile('photo.tif')
        self.file_data = file_handle.read()
        self.file_size = file_handle.tell()
        file_handle.seek(0)
        if self.implementation is not None:
            self.root.service_files.storage = self.implementation
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('testfile', 'Test File', file_handle)
        file_handle.close()

    def test_event(self):
        """Test that events are triggered.
        """
        # Clear events
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


    def test_content(self):
        """Test base content methods.
        """
        content = self.root.testfile
        self.failUnless(verifyObject(interfaces.IAsset, content))
        self.failUnless(verifyObject(interfaces.IFile, content))

        self.assertEquals(content.content_type(), 'image/tiff')
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'testfile')
        self.assertEquals(content.get_mime_type(), 'image/tiff')
        self.assertHashEqual(content.get_content(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)

        # If you change the filename, you will get the new value afterward
        content.set_filename('image.tiff')
        self.assertEquals(content.get_filename(), 'image.tiff')

    def test_download(self):
        """Test downloading file.
        """
        response = http('GET /root/testfile HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        downloaded_data = response.getBody()
        self.assertEquals(len(downloaded_data), self.file_size)
        self.assertHashEqual(downloaded_data, self.file_data)
        self.assertEquals(int(headers['Content-Length']), self.file_size)
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Disposition'],
                          'inline;filename=testfile')
        self.failUnless('Last-Modified' in headers)

    def test_not_modified(self):
        """Test downloading a file if it as been modified after a date.
        """
        response = http(
            'GET /root/testfile HTTP/1.1',
            parsed=True,
            headers={'If-Modified-Since': 'Sat, 29 Oct 2094 19:43:31 GMT'})
        self.assertEquals(response.getStatus(), 304)
        headers = response.getHeaders()
        self.assertEquals(len(response.getBody()), 0)

    def test_head_request(self):
        """Test HEAD requests on Files.
        """
        response = http('HEAD /root/testfile HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        # Even on HEAD requests where there is no body, Content-Lenght
        # should be the size of the file.
        self.assertEquals(int(headers['Content-Length']), self.file_size)
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Disposition'],
                          'inline;filename=testfile')
        self.failUnless('Last-Modified' in headers)
        self.assertEquals(len(response.getBody()), 0)

    def test_asset_data(self):
        """Test asset data adapter implementation.
        """
        content = self.root.testfile
        assetdata = interfaces.IAssetData(content)
        self.failUnless(verifyObject(interfaces.IAssetData, assetdata))
        self.assertHashEqual(self.file_data, assetdata.getData())


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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(BlobFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(ZODBFileImplementationTestCase))
    if File.FILESYSTEM_STORAGE_AVAILABLE:
        suite.addTest(unittest.makeSuite(FFSFileImplementationTestCase))
    return suite
