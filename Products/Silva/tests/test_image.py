# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

try:
    from PIL import Image as PILImage
except ImportError:
    import Image as PILImage
import unittest
import io

from DateTime import DateTime

from zope.interface.verify import verifyObject
from zope.component import getUtility

from silva.core import interfaces
from silva.core.services.interfaces import ICatalogService
from silva.core.services.interfaces import IMetadataService

from Products.Silva import File
from Products.Silva.testing import FunctionalLayer, TestCase, Transaction
from Products.Silva.testing import assertTriggersEvents


def search(**query):
    catalog = getUtility(ICatalogService)
    return map(lambda b: b.getPath(), catalog(**query))


class DefaultImageTestCase(TestCase):
    """Test images, switching storages.
    """
    layer = FunctionalLayer
    implementation = None

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        with Transaction():
            if self.implementation is not None:
                self.root.service_files.storage = self.implementation

            factory = self.root.manage_addProduct['Silva']
            with self.layer.open_fixture('photo.tif') as image:
                self.image_data = image.read()
                self.image_size = image.tell()
                image.seek(0, 0)

                factory.manage_addImage('test_image', u'Image élaboré', image)

        image = self.root._getOb('test_image')
        metadata = getUtility(IMetadataService).getMetadata(image)
        metadata.setValues('silva-extra', {
            'modificationtime': DateTime('2010-04-25T12:00:00Z')})

    def test_image(self):
        """Test image content.
        """
        image = self.root._getOb('test_image')
        self.assertTrue(verifyObject(interfaces.IAsset, image))
        self.assertTrue(verifyObject(interfaces.IImage, image))
        self.assertNotEqual(image.get_modification_datetime(), None)
        self.assertNotEqual(image.get_creation_datetime(), None)

        # Asset methods
        self.assertEquals(image.get_content_type(), 'image/tiff')
        self.assertEquals(image.get_file_size(), self.image_size)
        self.assertEquals(image.get_filename(), 'test_image.tiff')
        self.assertEquals(image.get_mime_type(), 'image/tiff')

        # Image methods
        self.assertTrue(image.get_html_tag() is not None)
        self.assertEquals(image.get_format(), 'TIFF')
        self.assertEquals(image.get_web_format(), 'JPEG')
        self.assertEquals(image.get_dimensions(), (960, 1280))
        self.assertEquals(str(image.get_orientation()), "portrait")
        self.assertEquals(
            image.get_download_url(),
            'http://localhost/root/test_image')

        image.set_web_presentation_properties('JPEG', '100x100', '')
        self.assertEquals(image.get_web_format(), 'JPEG')

        data = io.BytesIO(image.get_image(hires=False, webformat=True))
        pil_image = PILImage.open(data)
        self.assertEquals((100, 100), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

        data = image.get_image(hires=True, webformat=False)
        self.assertHashEqual(self.image_data, data)
        self.assertEquals(
            image.get_download_url(hires=True),
            'http://localhost/root/test_image?hires')

        data = io.BytesIO(image.get_image(hires=True, webformat=True))
        pil_image = PILImage.open(data)
        self.assertEquals((960, 1280), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

        with self.assertRaises(ValueError) as error:
            image.get_image(hires=False, webformat=False)
        self.assertEquals(
            str(error.exception),
            'Low resolution image in original format is not supported')

    def test_set_web_presentation_properties(self):
        """Test set web presentation.
        """
        image = self.root._getOb('test_image')
        original_dimensions = image.get_dimensions()

        ## resizing image to 200x100.
        image.set_web_presentation_properties('', '200x100', '')
        ## it should be 200x100 now.
        self.assertEquals((200, 100), image.get_dimensions())

        ## resizing passing an empty size paramenter.
        image.set_web_presentation_properties('', '', '')
        ## it should be back to the original size now (100%).
        self.assertEquals(original_dimensions, image.get_dimensions())

        ## resizing passing an invalid size parameter.
        image.set_web_presentation_properties('', 'invalid image size', '')
        ## it should still have the original size.
        self.assertEquals(original_dimensions, image.get_dimensions())

        ## resizing image to 370x230.
        image.set_web_presentation_properties('', '370x230', '')
        ## it should be 370x230 now.
        self.assertEquals((370, 230), image.get_dimensions())

        ## resizing passing an invalid size parameter (again).
        image.set_web_presentation_properties('', ' again an invalid image size ', '')
        ## it should be back to the original size now (100%).
        self.assertEquals(original_dimensions, image.get_dimensions())

    def test_add_image_with_existing_id(self):
        with Transaction():
            with self.layer.open_fixture('photo.tif') as image:
                factory = self.root.manage_addProduct['Silva']
                factory.manage_addImage('test_image_id', 'Test Image 1', image)
                with self.assertRaises(ValueError) as error:
                    factory.manage_addImage('test_image_id',
                                            'Test Image 2', image)

        self.assertEqual(
            str(error.exception),
            "Please provide a unique id: ${reason}")

    def test_rename_image(self):
        """Move an image and check that the filename is updated correctly.
        """
        image = self.root._getOb('test_image')
        self.assertEquals(image.get_filename(), 'test_image.tiff')
        self.root.manage_renameObjects(['test_image'], ['new_image.gif'])

        image = self.root._getOb('new_image.gif')
        self.assertEquals(image.get_filename(), 'new_image.tiff')

    def test_copy_paste_image(self):
        """Cut and paste an image. Check the filename is updated.
        """
        token = self.root.manage_copyObjects(['test_image'])
        self.root.manage_pasteObjects(token)

        self.assertTrue('copy_of_test_image' in self.root.objectIds())
        copy_of_content = self.root.copy_of_test_image
        self.assertEquals(
            copy_of_content.get_filename(),
            'copy_of_test_image.tiff')

    def test_catalog(self):
        """Verify that the image is properly catalogued.
        """
        with Transaction(catalog=False):
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')

            factory = self.root.folder.manage_addProduct['Silva']
            with self.layer.open_fixture('photo.tif') as image:
                factory.manage_addImage('image', 'Test Image', image)

        # Test that the image is catalogued (and not the sub-files)
        self.assertItemsEqual(
            search(path='/root/folder'),
            ['/root/folder',
             '/root/folder/image'])

    def test_catalog_transaction(self):
        """Verify that the image is properly catalogued.
        """
        with Transaction(catalog=True):
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')

            factory = self.root.folder.manage_addProduct['Silva']
            with self.layer.open_fixture('photo.tif') as image:
                factory.manage_addImage('image', 'Test Image', image)

        # Test that the image is catalogued (and not the sub-files)
        self.assertItemsEqual(
            search(path='/root/folder'),
            ['/root/folder',
             '/root/folder/image'])

    def test_asset_payload(self):
        """Test AssetPayload adapter.
        """
        payload = interfaces.IAssetPayload(self.root.test_image)
        self.assertTrue(verifyObject(interfaces.IAssetPayload, payload))
        self.assertEqual(payload.get_payload(), self.image_data)

    def test_http_download(self):
        """Retrieve the image, check the headers. Image headers should
        permit to cache the image.
        """
        data = self.root.test_image.image
        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/test_image'), 200)
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')
            self.assertEqual(
                browser.headers['Content-Type'],
                'image/jpeg')
            self.assertEquals(
                browser.headers['Content-Length'],
                str(data.get_file_size()))
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEquals(
                browser.headers['Cache-Control'],
                'max-age=86400, must-revalidate')
            image_data = browser.contents
            pil_image = PILImage.open(io.BytesIO(image_data))
            self.assertEqual((960, 1280), pil_image.size)
            self.assertEqual('JPEG', pil_image.format)
            self.assertHashEqual(data.get_file(), image_data)

    def test_http_download_hires(self):
        """Retrieve the image, check the headers. Image should be cached.
        """
        with self.layer.get_browser() as browser:
            self.assertEquals(browser.open('/root/test_image?hires'), 200)
            self.assertEquals(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.tiff')
            self.assertEquals(
                browser.headers['Content-Type'],
                'image/tiff')
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEquals(
                browser.headers['Cache-Control'],
                'max-age=86400, must-revalidate')
            image_data = browser.contents
            pil_image = PILImage.open(io.BytesIO(image_data))
            self.assertEquals((960, 1280), pil_image.size)
            self.assertEquals('TIFF', pil_image.format)
            self.assertHashEqual(self.image_data, image_data)

    def test_http_download_thumbnail(self):
        """Retrieve image thumbnail, check the headers. Caching should
        be enabled.
        """
        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/test_image?thumbnail'), 200)
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')
            self.assertEqual(
                browser.headers['Content-Type'],
                'image/jpeg')
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEquals(
                browser.headers['Cache-Control'],
                'max-age=86400, must-revalidate')
            body = browser.contents
            self.assertEqual(browser.headers['Content-Length'], str(len(body)))
            pil_image = PILImage.open(io.BytesIO(body))
            self.assertEqual((90, 120), pil_image.size)
            self.assertEqual('JPEG', pil_image.format)

    def test_http_preview_thumbnail(self):
        """If you access the preview of an image, the cache should be disabled.
        """
        with self.layer.get_browser() as browser:
            self.assertEqual(
                browser.open('/root/++preview++/test_image?thumbnail'), 200)
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')
            self.assertEqual(
                browser.headers['Content-Type'],
                'image/jpeg')
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEquals(
                browser.headers['Pragma'],
                'no-cache')
            self.assertEquals(
                browser.headers['Cache-Control'],
                'no-cache, must-revalidate, post-check=0, pre-check=0')
            body = browser.contents
            self.assertEqual(browser.headers['Content-Length'], str(len(body)))
            pil_image = PILImage.open(io.BytesIO(body))
            self.assertEqual((90, 120), pil_image.size)
            self.assertEqual('JPEG', pil_image.format)

    def test_http_head(self):
        """Do an HEAD request.
        """
        data = self.root.test_image.image
        with self.layer.get_browser() as browser:
            browser.options.handle_errors = False
            self.assertEquals(
                browser.open('/root/test_image', method='HEAD'), 200)
            self.assertEquals(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')
            self.assertEquals(
                browser.headers['Content-Type'],
                'image/jpeg')
            self.assertEquals(
                browser.headers['Content-Length'],
                str(data.get_file_size()))
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEquals(browser.contents, '')

    def test_http_head_thumbnail(self):
        """Do an HEAD request on a thumbnail.
        """
        with self.layer.get_browser() as browser:
            self.assertEquals(
                browser.open('/root/test_image?thumbnail', method='HEAD'),
                200)
            self.assertEquals(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')
            self.assertEquals(
                browser.headers['Content-Type'],
                'image/jpeg')
            self.assertNotEqual(
                browser.headers['Content-Length'],
                '0')
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEquals(browser.contents, '')

    def test_http_head_hires(self):
        """Do an HEAD request.
        """
        with self.layer.get_browser() as browser:
            self.assertEquals(
                browser.open('/root/test_image?hires', method='HEAD'),
                200)
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.tiff')
            self.assertEqual(browser.headers['Content-Type'], 'image/tiff')
            self.assertEqual(
                browser.headers['Content-Length'],
                str(self.image_size))
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertIn(
                browser.headers['Accept-Ranges'],
                ('none', 'bytes'))
            self.assertEqual(len(browser.contents), 0)

    def test_http_not_modified(self):
        """Retrieve the image if it has been modified after a certain date.
        """
        with self.layer.get_browser() as browser:
            browser.set_request_header(
                'If-Modified-Since',
                'Sat, 29 Oct 2094 19:43:31 GMT')
            self.assertEqual(browser.open('/root/test_image'), 304)
            self.assertEqual(len(browser.contents), 0)

    def test_http_not_modified_thumbmail(self):
        """Retrieve the image if it has been modified after a certain date.
        """
        with self.layer.get_browser() as browser:
            browser.set_request_header(
                'If-Modified-Since',
                'Sat, 29 Oct 2094 19:43:31 GMT')
            self.assertEqual(browser.open('/root/test_image?thumbnail'), 304)
            self.assertEqual(len(browser.contents), 0)

    def test_http_not_modified_hires(self):
        """Retrieve the image if it has been modified after a certain date.
        """
        with self.layer.get_browser() as browser:
            browser.set_request_header(
                'If-Modified-Since',
                'Sat, 29 Oct 2094 19:43:31 GMT')
            self.assertEqual(browser.open('/root/test_image?hires'), 304)
            self.assertEqual(len(browser.contents), 0)


class ZODBImageTestCase(DefaultImageTestCase):
    """Test image with ZODB storage.
    """
    implementation = File.ZODBFile


class BlobImageTestCase(DefaultImageTestCase):
    """Test image with ZODB storage.
    """
    implementation = File.BlobFile

    def test_http_download_range(self):
        """Test downloading only a range of a file.
        """
        file_size = self.root.test_image.image.get_file_size()
        with self.layer.get_browser() as browser:
            browser.set_request_header('Range', 'bytes=100-500')
            self.assertEqual(browser.open('/root/test_image'), 206)
            self.assertEqual(len(browser.contents), 400)
            self.assertEqual(browser.headers['Content-Length'], '400')
            self.assertEqual(browser.headers['Content-Type'], 'image/jpeg')
            self.assertEqual(
                browser.headers['Content-Range'],
                'bytes 100-500/%s' % file_size)
            self.assertEqual(browser.headers['Accept-Ranges'], 'bytes')
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')

    def test_http_download_invalid_range(self):
        file_size = self.root.test_image.image.get_file_size()
        with self.layer.get_browser() as browser:
            browser.set_request_header('Range', 'bytes=4000000-5000000')
            self.assertEqual(browser.open('/root/test_image'), 416)
            self.assertEqual(len(browser.contents), 0)
            self.assertEqual(browser.headers['Content-Type'], 'image/jpeg')
            self.assertEqual(
                browser.headers['Content-Length'],
                str(file_size))
            self.assertEqual(
                browser.headers['Content-Range'],
                'bytes */%s' % file_size)
            self.assertEqual(browser.headers['Accept-Ranges'], 'bytes')
            self.assertEquals(
                browser.headers['Last-Modified'],
                'Sun, 25 Apr 2010 12:00:00 GMT')
            self.assertEqual(
                browser.headers['Content-Disposition'],
                'inline;filename=test_image.jpeg')


class MiscellaneousImageTestCase(unittest.TestCase):
    """Test miscellaneous image features.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def test_empty_image(self):
        """Test an image that doesn't store an image.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            with assertTriggersEvents('ObjectCreatedEvent'):
                factory.manage_addImage('image', 'Image')

        image = self.root.image
        self.assertTrue(verifyObject(interfaces.IImage, image))
        self.assertEqual(image.get_mime_type(), 'application/octet-stream')
        self.assertEqual(image.get_content_type(), 'application/octet-stream')
        self.assertEqual(image.get_filename(), 'image')
        self.assertEqual(image.get_file_size(), 0)
        self.assertEqual(image.get_file_system_path(), None)
        self.assertEqual(image.get_image(), None)
        self.assertNotEqual(image.get_modification_datetime(), None)
        self.assertNotEqual(image.get_creation_datetime(), None)

        payload = interfaces.IAssetPayload(image)
        self.assertTrue(verifyObject(interfaces.IAssetPayload, payload))
        self.assertEqual(payload.get_payload(), None)

        # Since the image is empty, a request to it will trigger a 404
        with self.layer.get_browser() as browser:
            self.assertEqual(browser.open('/root/image'), 404)

    def test_invalid_image(self):
        """Try to add an non-image.
        """
        image = io.BytesIO('invalid-image-format')
        factory = self.root.manage_addProduct['Silva']
        with self.assertRaises(ValueError):
            factory.manage_addImage('badimage', 'Bad Image', image)

        self.assertFalse('badimage' in self.root.objectIds())

    def test_get_crop_box(self):
        """Test get_crop_box method that either return or parse a crop_box.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            with self.layer.open_fixture('photo.tif') as image:
                factory.manage_addImage('image', 'Torvald', image)

        self.assertEqual(
            self.root.image.get_crop_box(crop="242x379-392x479"),
            (242, 379, 392, 479))
        self.assertEqual(
            self.root.image.get_crop_box(crop="392x479-242x379"),
            (242, 379, 392, 479))
        # To big for the given image
        self.assertRaises(
            ValueError,
            self.root.image.get_crop_box, crop="26000x8000-1280x2800")
        self.assertRaises(
            ValueError,
            self.root.image.get_crop_box, crop="santa clauss")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultImageTestCase))
    suite.addTest(unittest.makeSuite(ZODBImageTestCase))
    suite.addTest(unittest.makeSuite(BlobImageTestCase))
    suite.addTest(unittest.makeSuite(MiscellaneousImageTestCase))
    return suite
