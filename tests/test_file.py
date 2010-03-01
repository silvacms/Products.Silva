# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope import component
from zope.interface.verify import verifyObject
from Testing.ZopeTestCase.zopedoctest.functional import http

from Products.Silva import File
from Products.Silva.tests import SilvaTestCase
from Products.Silva.tests import helpers
from silva.core import interfaces


class DefaultFileImplementationTestCase(SilvaTestCase.SilvaFunctionalTestCase):
    """Test default file implementation.
    """

    implementation = None

    def afterSetUp(self):
        file_handle = helpers.openTestFile('photo.tif')
        self.file_data = file_handle.read()
        self.file_size = file_handle.tell()
        file_handle.seek(0)
        if self.implementation is not None:
            self.root.service_files.storage = self.implementation
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('testfile', 'Test File', file_handle)
        file_handle.close()

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
        self.assertHashEquals(content.get_content(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)

        # If you change the filename, you will get the new value afterward
        content.set_filename('image.tiff')
        self.assertEquals(content.get_filename(), 'image.tiff')

    def test_download(self):
        """Test downloading file.
        """

        response = http('GET /root/testfile HTTP/1.1')
        headers = response.header_output.headers
        downloaded_data = response.getBody()
        self.assertEquals(len(downloaded_data), self.file_size)
        self.assertHashEquals(downloaded_data, self.file_data)
        self.assertEquals(int(headers['Content-Length']), self.file_size)
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Disposition'],
                          'inline;filename=testfile')

    def test_head_request(self):
        """Test HEAD requests on Files.
        """
        response = http('HEAD /root/testfile HTTP/1.1')
        headers = response.header_output.headers
        self.assertEquals(headers['Content-Length'], '0')
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Disposition'],
                          'inline;filename=testfile')

    def test_assetdata(self):
        """Test asset data adapter implementation.
        """
        content = self.root.testfile
        assetdata = interfaces.IAssetData(content)
        self.failUnless(verifyObject(interfaces.IAssetData, assetdata))
        self.assertHashEquals(self.file_data, assetdata.getData())


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
