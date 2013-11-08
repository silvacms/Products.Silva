# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import sys

from DateTime import DateTime

from zope.component import getUtility
from zope.interface.verify import verifyObject

from Products.Silva import File
from Products.Silva.File.converters import have_command
from Products.Silva.testing import FunctionalLayer, TestCase, tests, Transaction
from silva.core import interfaces
from silva.core.services.interfaces import IMetadataService


class ConverterTestCase(unittest.TestCase):
    """Test file converter utilities
    """

    def test_have_command(self):
        # Should not have a command that doesn't exist
        self.assertFalse(have_command('i_do_not_exists_silva_test'))
        # But you should have the python interpretor you are using
        self.assertTrue(have_command(sys.executable, '--version'))


class DefaultFileImplementationTestCase(TestCase):
    """Test default file implementation.
    """
    layer = FunctionalLayer
    implementation = None

    def setUp(self):
        with Transaction():
            self.root = self.layer.get_application()
            if self.implementation is not None:
                self.root.service_files.storage = self.implementation
        self.layer.login('author')

    def create_test_file(self, filename='photo.tif'):
        with Transaction():
            with self.layer.open_fixture(filename) as stream:
                self.file_data = stream.read()
                self.file_size = stream.tell()
                stream.seek(0)
                with tests.assertTriggersEvents(
                    'ObjectWillBeAddedEvent', 'ObjectAddedEvent',
                    'ContainerModifiedEvent', 'ObjectCreatedEvent'):
                    factory = self.root.manage_addProduct['Silva']
                    factory.manage_addFile(filename, 'Test File', stream)
        content =  self.root._getOb(filename)
        metadata = getUtility(IMetadataService).getMetadata(content)
        metadata.setValues('silva-extra', {
                'modificationtime': DateTime('2010-04-25T12:00:00Z')})
        return content

    def test_upload_file_with_existing_id(self):
        """Test whether a file upload with a duplicate ID throws a ValueError
        """
        factory = self.root.manage_addProduct['Silva']

        with self.layer.open_fixture('photo.tif') as test_file:
            factory.manage_addFile('test_file_id', 'Test File 1', test_file)
            with self.assertRaises(ValueError) as error:
                factory.manage_addImage(
                    'test_file_id', 'Test File 2', test_file)

        self.assertEqual(
            str(error.exception),
            "Please provide a unique id: ${reason}")

        with self.layer.open_fixture('photo.tif') as test_file:
            factory.manage_addFile(
                'test_file_unique_id', 'Test File 3', test_file)

        content = self.root._getOb('test_file_unique_id')
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

    def test_content_image(self):
        """Test base content methods on a file that contains an image.
        """
        content = self.create_test_file()
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        self.assertEqual(content.get_content_type(), 'image/tiff')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_file_size(), self.file_size)
        self.assertEqual(content.get_filename(), 'photo.tif')
        self.assertEqual(content.get_mime_type(), 'image/tiff')
        self.assertHashEqual(content.get_file(), self.file_data)
        self.assertTrue(content.get_download_url() is not None)
        self.assertTrue(content.tag() is not None)
        # You cannot edit images as text
        self.assertEqual(content.is_text(), False)

        # If you change the filename, you will get the new value afterward
        content.set_filename('image.tiff')
        self.assertEqual(content.get_filename(), 'image.tiff')

    def test_content_zip(self):
        """Test base content methods on a file that contains an image.
        """
        content = self.create_test_file('test1.zip')
        self.failUnless(verifyObject(interfaces.IAsset, content))
        self.failUnless(verifyObject(interfaces.IFile, content))

        self.assertEquals(content.get_content_type(), 'application/zip')
        self.assertEquals(content.get_content_encoding(), None)
        self.assertEquals(content.get_file_size(), self.file_size)
        self.assertEquals(content.get_filename(), 'test1.zip')
        self.assertEquals(content.get_mime_type(), 'application/zip')
        self.assertHashEqual(content.get_file(), self.file_data)
        self.failUnless(content.get_download_url() is not None)
        self.failUnless(content.tag() is not None)
        # You cannot edit zip as text
        self.assertEquals(content.is_text(), False)

    def test_content_text(self):
        """Test base content methods on a file that contains text.
        """
        content = self.create_test_file('test_file_text.txt')
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        self.assertEqual(content.get_content_type(), 'text/plain; charset=utf-8')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_file_size(), self.file_size)
        self.assertEqual(content.get_filename(), 'test_file_text.txt')
        self.assertEqual(content.get_mime_type(), 'text/plain')
        self.assertHashEqual(content.get_file(), self.file_data)
        self.assertTrue(content.get_download_url() is not None)
        self.assertTrue(content.tag() is not None)
        # You can edit text
        self.assertEqual(content.is_text(), True)
        self.assertEqual(content.is_text_editable(), True)

        # If you change the filename, you will get the new value afterward
        content.set_filename('text.txt')
        self.assertEqual(content.get_filename(), 'text.txt')

        # You can change the text of a text file.
        content.set_text("This is the story of a kind")
        self.assertEqual(content.get_file_size(), 27)
        # XXX This triggered object modified and reseted the filename.
        self.assertEqual(content.get_filename(), 'test_file_text.txt')
        self.assertEqual(content.get_content_type(), 'text/plain; charset=utf-8')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_mime_type(), 'text/plain')
        self.assertEqual(content.is_text(), True)
        self.assertEqual(content.is_text_editable(), True)

    def test_content_compressed_text(self):
        """Test base content methods on a file that contains
        compressed text.
        """
        content = self.create_test_file('test_file_text.txt.gz')
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        self.assertEqual(content.get_content_type(), 'text/plain; charset=utf-8')
        self.assertEqual(content.get_content_encoding(), 'gzip')
        self.assertEqual(content.get_file_size(), self.file_size)
        self.assertEqual(content.get_filename(), 'test_file_text.txt.gz')
        self.assertEqual(content.get_mime_type(), 'text/plain')
        self.assertHashEqual(content.get_file(), self.file_data)
        self.assertTrue(content.get_download_url() is not None)
        self.assertTrue(content.tag() is not None)
        # You cannot edit compressed files
        self.assertEqual(content.is_text(), False)

    def test_content_xml(self):
        """Test base content methods on a file that contains xml.
        """
        content = self.create_test_file('test_document.xml')
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        self.assertEqual(content.get_content_type(), 'application/xml')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_file_size(), self.file_size)
        self.assertEqual(content.get_filename(), 'test_document.xml')
        self.assertEqual(content.get_mime_type(), 'application/xml')
        self.assertHashEqual(content.get_file(), self.file_data)
        self.assertTrue(content.get_download_url() is not None)
        self.assertTrue(content.tag() is not None)
        # You can edit text
        self.assertEqual(content.is_text(), True)

    def test_modify_text(self):
        """Test changing the text of a text editable file.
        """
        content = self.create_test_file('test_file_text.txt')
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        self.assertEqual(content.get_content_type(), 'text/plain; charset=utf-8')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_file_size(), self.file_size)
        self.assertEqual(content.get_filename(), 'test_file_text.txt')
        self.assertEqual(content.get_mime_type(), 'text/plain')

        # You can edit text
        self.assertEqual(content.is_text(), True)
        self.assertEqual(content.is_text_editable(), True)

        # You can change the text of a text file.
        with tests.assertTriggersEvents('ObjectModifiedEvent'):
            content.set_text("This is the story of a kind")

        self.assertEqual(content.get_file_size(), 27)
        self.assertEqual(content.get_filename(), 'test_file_text.txt')
        self.assertEqual(content.get_content_type(), 'text/plain; charset=utf-8')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_mime_type(), 'text/plain')
        self.assertEqual(content.is_text(), True)
        self.assertEqual(content.is_text_editable(), True)

    def test_modify_file(self):
        """Test uploading a file with a new one. The new content type
        and content encoding should have been detected.
        """
        content = self.create_test_file()
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        # We have an image.
        self.assertEqual(content.get_content_type(), 'image/tiff')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_filename(), 'photo.tif')
        self.assertEqual(content.get_mime_type(), 'image/tiff')

        # Now we upload a text file.
        with self.layer.open_fixture('test_document.xml') as stream:
            with tests.assertTriggersEvents('ObjectModifiedEvent'):
                content.set_file(stream)

        # We didn't specify any content_type of encoding, they should
        # have been detected.
        self.assertEqual(content.get_content_type(), 'application/xml')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_filename(), 'photo.xml')
        self.assertEqual(content.get_mime_type(), 'application/xml')

    def test_modify_file_and_content_type(self):
        """Test uploading a file with a new one. The content type
        given as option should be used, and no content type or content
        encoding should be detected.
        """
        content = self.create_test_file()
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IFile, content))

        # We have an image.
        self.assertEqual(content.get_content_type(), 'image/tiff')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_filename(), 'photo.tif')
        self.assertEqual(content.get_mime_type(), 'image/tiff')

        # Now we upload a text file.
        with self.layer.open_fixture('test_document.xml') as stream:
            with tests.assertTriggersEvents('ObjectModifiedEvent'):
                content.set_file(stream, content_type='text/html')

        # We have the new content_type and content encoding, even if
        # they don't match the file
        self.assertEqual(content.get_content_type(), 'text/html')
        self.assertEqual(content.get_content_encoding(), None)
        self.assertEqual(content.get_filename(), 'photo.html')
        self.assertEqual(content.get_mime_type(), 'text/html')

    def test_download(self):
        """Test downloading file.
        """
        self.create_test_file()
        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/photo.tif'), 200)
            self.assertEqual(len(browser.contents), self.file_size)
            self.assertHashEqual(browser.contents, self.file_data)
            self.assertEqual(
                int(browser.headers['Content-Length']),
                self.file_size)
            self.assertEqual(browser.headers['Content-Type'], 'image/tiff')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=photo.tif')
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))

    def test_download_not_modified(self):
        """Test downloading a file if it as been modified after a date.
        """
        self.create_test_file()
        with self.layer.get_browser() as browser:
            browser.set_request_header(
                'If-Modified-Since', 'Sat, 29 Oct 2094 19:43:31 GMT')
            self.assertEqual(browser.open('/root/photo.tif'), 304)
            self.assertEqual(len(browser.contents), 0)

    def test_head_request(self):
        """Test HEAD requests on Files.
        """
        self.create_test_file()
        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/photo.tif', method='HEAD'), 200)
            # Even on HEAD requests where there is no body, Content-Lenght
            # should be the size of the file.
            self.assertEqual(
                int(browser.headers['Content-Length']),
                self.file_size)
            self.assertEqual(
                browser.headers['Content-Type'],
                'image/tiff')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=photo.tif')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(len(browser.contents), 0)

    def test_asset_payload(self):
        """Test asset data adapter implementation.
        """
        content = self.create_test_file()
        payload = interfaces.IAssetPayload(content)
        self.assertTrue(verifyObject(interfaces.IAssetPayload, payload))
        self.assertHashEqual(self.file_data, payload.get_payload())

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

    def test_download_range(self):
        """Test downloading only a range of a file.
        """
        self.create_test_file()
        with self.layer.get_browser() as browser:
            browser.set_request_header('Range', 'bytes=100-500')
            self.assertEqual(browser.open('/root/photo.tif'), 206)
            self.assertEqual(len(browser.contents), 400)
            self.assertEqual(browser.headers['Content-Length'], '400')
            self.assertEqual(browser.headers['Content-Type'], 'image/tiff')
            self.assertEqual(
                browser.headers['Content-Range'],
                'bytes 100-500/%s' % self.file_size)
            self.assertEqual(browser.headers['Accept-Ranges'], 'bytes')
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=photo.tif')

    def test_download_range_if_match(self):
        """Test download a range of a file with an If-Range header.
        """
        self.create_test_file()
        with self.layer.get_browser() as browser:
            browser.set_request_header('Range', 'bytes=100-500')
            browser.set_request_header('If-Range', 'Wed, 23 Jun 2010 12:00:00 GMT')
            self.assertEqual(browser.open('/root/photo.tif'), 206)
            self.assertEqual(len(browser.contents), 400)
            self.assertEqual(browser.headers['Content-Length'], '400')
            self.assertEqual(browser.headers['Content-Type'], 'image/tiff')
            self.assertEqual(
                browser.headers['Content-Range'],
                'bytes 100-500/%s' % self.file_size)
            self.assertEqual(browser.headers['Accept-Ranges'], 'bytes')
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=photo.tif')

    def test_download_range_if_not_match(self):
        """Test download a range of a file with an If-Range header.
        """
        self.create_test_file()
        with self.layer.get_browser() as browser:
            browser.set_request_header('Range', 'bytes=100-500')
            browser.set_request_header('If-Range', 'Sat, 23 Jun 2001 12:00:00 GMT')
            self.assertEqual(browser.open('/root/photo.tif'), 200)
            self.assertEqual(len(browser.contents), self.file_size)
            self.assertEqual(browser.headers['Content-Type'], 'image/tiff')
            self.assertEqual(browser.headers['Accept-Ranges'], 'bytes')
            self.assertNotIn('Content-Range', browser.headers)
            self.assertEqual(
                browser.headers['Content-Length'],
                str(self.file_size))
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=photo.tif')

    def test_download_invalid_range(self):
        self.create_test_file()
        with self.layer.get_browser() as browser:
            browser.set_request_header('Range', 'bytes=4000000-5000000')
            self.assertEqual(browser.open('/root/photo.tif'), 416)
            self.assertEqual(len(browser.contents), 0)
            self.assertEqual(browser.headers['Content-Type'], 'image/tiff')
            self.assertEqual(
                browser.headers['Content-Length'],
                str(self.file_size))
            self.assertEqual(
                browser.headers['Content-Range'],
                'bytes */%s' % self.file_size)
            self.assertEqual(browser.headers['Accept-Ranges'], 'bytes')
            self.assertEqual(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=photo.tif')



class ZODBFileImplementationTestCase(DefaultFileImplementationTestCase):
    """Test ZODB file implementation.
    """
    implementation = File.ZODBFile



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConverterTestCase))
    suite.addTest(unittest.makeSuite(DefaultFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(BlobFileImplementationTestCase))
    suite.addTest(unittest.makeSuite(ZODBFileImplementationTestCase))
    return suite
