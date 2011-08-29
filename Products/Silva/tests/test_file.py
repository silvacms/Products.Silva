# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO
import unittest

from zope.interface.verify import verifyObject

from Products.Silva import File
from Products.Silva.helpers import create_new_filename
from Products.Silva.testing import FunctionalLayer, TestCase, get_event_names
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

        file_handle = helpers.open_test_file('photo.tif')
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
             'MetadataModifiedEvent',
             'ObjectCreatedEvent', 'MetadataModifiedEvent'])

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
        self.assertEquals(content.content_encoding(), None)
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'testfile.tiff')
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
        with self.layer.get_browser() as browser:
            self.assertEquals(browser.open('/root/testfile'), 200)
            self.assertEquals(len(browser.contents), self.file_size)
            self.assertHashEqual(browser.contents, self.file_data)
            self.assertEquals(
                int(browser.headers['Content-Length']),
                self.file_size)
            self.assertEquals(browser.headers['Content-Type'], 'image/tiff')
            self.assertEquals(
                browser.headers['Content-Disposition'],
                'inline;filename=testfile.tiff')
            self.failUnless('Last-Modified' in browser.headers)

    def test_not_modified(self):
        """Test downloading a file if it as been modified after a date.
        """
        with self.layer.get_browser() as browser:
            browser.set_request_header(
                'If-Modified-Since', 'Sat, 29 Oct 2094 19:43:31 GMT')
            self.assertEquals(browser.open('/root/testfile'), 304)
            self.assertEquals(len(browser.contents), 0)

    def test_head_request(self):
        """Test HEAD requests on Files.
        """
        with self.layer.get_browser() as browser:
            self.assertEquals(browser.open('/root/testfile', method='HEAD'), 200)
            # Even on HEAD requests where there is no body, Content-Lenght
            # should be the size of the file.
            self.assertEquals(
                int(browser.headers['Content-Length']),
                self.file_size)
            self.assertEquals(browser.headers['Content-Type'], 'image/tiff')
            self.assertEquals(
                browser.headers['Content-Disposition'],
                'inline;filename=testfile.tiff')
            self.failUnless('Last-Modified' in browser.headers)
            self.assertEquals(len(browser.contents), 0)

    def test_asset_data(self):
        """Test asset data adapter implementation.
        """
        content = self.root.testfile
        assetdata = interfaces.IAssetData(content)
        self.failUnless(verifyObject(interfaces.IAssetData, assetdata))
        self.assertHashEqual(self.file_data, assetdata.getData())

    def test_rename_filename(self):
        """If you rename the file, the filename gets updated, and
        replace any existing wrong extension.
        """
        self.root.manage_renameObject('testfile', 'renamedfile')
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


class CreateNewFilenameTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def create_file(self, filename):
        with helpers.open_test_file(filename) as file_handle:
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFile('testfile', 'Test File', file_handle)
            return self.root.testfile

    def test_image_png_filename(self):
        testfile = self.create_file('photo.tif')

        create_new_filename(testfile, 'image')
        self.assertEqual(testfile.get_filename(), 'image.tiff')

    def test_image_png_filename_with_extension(self):
        testfile = self.create_file('photo.tif')

        create_new_filename(testfile, 'image.jpg')
        self.assertEqual(testfile.get_filename(), 'image.tiff')

    def test_tar_gz_filename(self):
        testfile = self.create_file('images.tar.gz')

        create_new_filename(testfile, 'files')
        self.assertEqual(testfile.get_filename(), 'files.gz')

    def test_tar_gz_filename_with_partial_extension(self):
        testfile = self.create_file('images.tar.gz')

        create_new_filename(testfile, 'files.tar')
        self.assertEqual(testfile.get_filename(), 'files.tar.gz')

    def test_tar_gz_filename_with_extension(self):
        testfile = self.create_file('images.tar.gz')

        create_new_filename(testfile, 'files.tar.gz')
        self.assertEqual(testfile.get_filename(), 'files.tar.gz')

    def test_zip_filename(self):
        testfile = self.create_file('test1.zip')

        create_new_filename(testfile, 'files')
        self.assertEqual(testfile.get_filename(), 'files.zip')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CreateNewFilenameTestCase))
    suite.addTest(unittest.makeSuite(DefaultFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(BlobFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(ZODBFileImplementationTestCase))
    return suite
