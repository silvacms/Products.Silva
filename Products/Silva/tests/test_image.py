# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from __future__ import absolute_import

from StringIO import StringIO
try:
    from PIL import Image as PILImage
except ImportError:
    import Image as PILImage
import unittest

from zope.interface.verify import verifyObject
from silva.core import interfaces

from Products.Silva import File
from Products.Silva.testing import FunctionalLayer, http, TestCase
from Products.Silva.testing import assertTriggersEvents
from Products.Silva.tests.helpers import open_test_file


class DefaultImageTestCase(TestCase):
    """Test images, switching storages.
    """
    layer = FunctionalLayer
    implementation = None

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

        image_file = open_test_file('photo.tif')
        self.image_data = image_file.read()
        self.image_size = image_file.tell()
        image_file.seek(0, 0)
        if self.implementation is not None:
            self.root.service_files.storage = self.implementation

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addImage('test_image', 'Test Image', image_file)
        image_file.close()

    def test_content(self):
        """Test image content.
        """
        content = self.root.test_image
        self.assertTrue(verifyObject(interfaces.IAsset, content))
        self.assertTrue(verifyObject(interfaces.IImage, content))

        # Asset methods
        self.assertEquals(content.content_type(), 'image/tiff')
        self.assertEquals(content.get_file_size(), self.image_size)
        self.assertEquals(content.get_filename(), 'test_image.tiff')
        self.assertEquals(content.get_mime_type(), 'image/tiff')

        # Image methods
        self.assertEquals(content.get_format(), 'TIFF')
        self.assertEquals(content.get_dimensions(), (960, 1280))
        self.assertEquals(str(content.get_orientation()), "portrait")
        content.set_web_presentation_properties('JPEG', '100x100', '')
        self.assertRaises(ValueError, content.get_image, hires=0, webformat=0)
        self.assertTrue(content.tag() is not None)

        data = StringIO(content.get_image(hires=0, webformat=1))
        pil_image = PILImage.open(data)
        self.assertEquals((100, 100), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

        data = content.get_image(hires=1, webformat=0)
        self.assertEquals(self.image_data, data)

        data = StringIO(content.get_image(hires=1, webformat=1))
        pil_image = PILImage.open(data)
        self.assertEquals((960, 1280), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

    def test_rename_content(self):
        """Move an image and check that the filename is updated correctly.
        """
        content = getattr(self.root, 'test_image')
        self.assertEquals(content.get_filename(), 'test_image.tiff')
        self.root.manage_renameObjects(['test_image'], ['new_image.gif'])

        content = getattr(self.root, 'new_image.gif')
        self.assertEquals(content.get_filename(), 'new_image.tiff')

    def test_copy_paste_content(self):
        """Cut and paste an image. Check the filename is updated.
        """
        token = self.root.manage_copyObjects(['test_image'])
        self.root.manage_pasteObjects(token)

        self.assertTrue('copy_of_test_image' in self.root.objectIds())
        copy_of_content = self.root.copy_of_test_image
        self.assertEquals(
            copy_of_content.get_filename(),
            'copy_of_test_image.tiff')

    def test_asset_data(self):
        """Test AssetData adapter.
        """
        asset_data = interfaces.IAssetData(self.root.test_image)
        self.assertTrue(verifyObject(interfaces.IAssetData, asset_data))
        self.assertEquals(self.image_data, asset_data.getData())

    def test_http_view(self):
        """Retrieve the image, check the headers.
        """
        response = http('GET /root/test_image HTTP/1.1', parsed=True)
        self.assertEqual(response.getStatus(), 200)
        headers = response.getHeaders()
        self.assertEqual(
            headers['Content-Disposition'], 'inline;filename=test_image.tiff')
        self.assertEqual(headers['Content-Type'], 'image/tiff')
        self.assertTrue('Last-Modified' in headers)
        image_data = response.getBody()
        pil_image = PILImage.open(StringIO(image_data))
        self.assertEqual((960, 1280), pil_image.size)
        self.assertEqual('TIFF', pil_image.format)
        self.assertHashEqual(self.image_data, image_data)

    def test_http_view_hires(self):
        """Retrieve the image, check the headers.
        """
        response = http('GET /root/test_image?hires HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        self.assertEquals(
            headers['Content-Disposition'], 'inline;filename=test_image.tiff')
        self.assertEquals(
            headers['Content-Type'], 'image/tiff')
        image_data = response.getBody()
        pil_image = PILImage.open(StringIO(image_data))
        self.assertEquals((960, 1280), pil_image.size)
        self.assertEquals('TIFF', pil_image.format)
        self.assertHashEqual(self.image_data, image_data)

    def test_http_view_thumbnail(self):
        """Retrieve image thumbnail, check the headers.
        """
        response = http('GET /root/test_image?thumbnail HTTP/1.1', parsed=True)
        self.assertEqual(response.getStatus(), 200)
        headers = response.getHeaders()
        self.assertEqual(
            headers['Content-Disposition'], 'inline;filename=test_image.jpeg')
        self.assertEqual(headers['Content-Type'], 'image/jpeg')
        body = response.getBody()
        self.assertEqual(headers['Content-Length'], str(len(body)))
        pil_image = PILImage.open(StringIO(body))
        self.assertEqual((90, 120), pil_image.size)
        self.assertEqual('JPEG', pil_image.format)

    def test_http_head(self):
        """Do an HEAD request.
        """
        response = http('HEAD /root/test_image HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        self.assertEquals(
            headers['Content-Disposition'], 'inline;filename=test_image.tiff')
        self.assertEquals(headers['Content-Type'], 'image/tiff')
        self.assertEquals(headers['Content-Length'], str(self.image_size))
        self.assertTrue('Last-Modified' in headers)
        self.assertEquals(response.getBody(), '')

    def test_http_head_thumbnail(self):
        """Do an HEAD request on a thumbnail.
        """
        response = http('HEAD /root/test_image?thumbnail HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        self.assertEquals(
            headers['Content-Disposition'], 'inline;filename=test_image.jpeg')
        self.assertEquals(headers['Content-Type'], 'image/jpeg')
        self.assertNotEqual(headers['Content-Length'], '0')
        self.assertEquals(response.getBody(), '')

    def test_http_head_hires(self):
        """Do an HEAD request.
        """
        response = http('HEAD /root/test_image?hires HTTP/1.1', parsed=True)
        self.assertEquals(response.getStatus(), 200)
        headers = response.getHeaders()
        self.assertEqual(
            headers['Content-Disposition'], 'inline;filename=test_image.tiff')
        self.assertEqual(headers['Content-Type'], 'image/tiff')
        self.assertEqual(headers['Content-Length'], str(self.image_size))
        self.assertEqual(len(response.getBody()), 0)

    def test_http_not_modified(self):
        """Retrieve the image if it has been modified after a certain date.
        """
        response = http(
            'GET /root/test_image HTTP/1.1',
            parsed=True,
            headers={'If-Modified-Since': 'Sat, 29 Oct 2094 19:43:31 GMT'})
        self.assertEqual(response.getStatus(), 304)
        self.assertEqual(len(response.getBody()), 0)

    def test_http_not_modified_thumbmail(self):
        """Retrieve the image if it has been modified after a certain date.
        """
        response = http(
            'GET /root/test_image?thumbnail HTTP/1.1',
            parsed=True,
            headers={'If-Modified-Since': 'Sat, 29 Oct 2094 19:43:31 GMT'})
        self.assertEqual(response.getStatus(), 304)
        self.assertEqual(len(response.getBody()), 0)

    def test_http_not_modified_hires(self):
        """Retrieve the image if it has been modified after a certain date.
        """
        response = http(
            'GET /root/test_image?hires HTTP/1.1',
            parsed=True,
            headers={'If-Modified-Since': 'Sat, 29 Oct 2094 19:43:31 GMT'})
        self.assertEqual(response.getStatus(), 304)
        self.assertEqual(len(response.getBody()), 0)


class ZODBImageTestCase(DefaultImageTestCase):
    """Test image with ZODB storage.
    """
    implementation = File.ZODBFile


class BlobImageTestCase(DefaultImageTestCase):
    """Test image with ZODB storage.
    """
    implementation = File.BlobFile


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
        factory = self.root.manage_addProduct['Silva']
        with assertTriggersEvents('ObjectCreatedEvent'):
            factory.manage_addImage('image', 'Image')

        image = self.root.image
        self.assertTrue(verifyObject(interfaces.IImage, image))
        self.assertEqual(image.get_mime_type(), 'application/octet-stream')
        self.assertEqual(image.content_type(), 'application/octet-stream')
        self.assertEqual(image.get_filename(), 'image')
        self.assertEqual(image.get_file_size(), 0)

    def test_invalid_image(self):
        """Try to add an non-image.
        """
        image_file = StringIO('invalid-image-format')
        factory = self.root.manage_addProduct['Silva']
        self.assertRaises(
            ValueError,
            factory.manage_addImage, 'badimage', 'Bad Image', image_file)
        self.assertFalse('badimage' in self.root.objectIds())

    def test_get_crop_box(self):
        """Test get_crop_box method that either return or parse a crop_box.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addImage('image', 'Torvald', open_test_file('photo.tif'))
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


class ImageFunctionalTest(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        image, image_data = self.add_test_image()
        # XXX Need to add test for this
        image.set_web_presentation_properties('JPEG', '100x100', '')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultImageTestCase))
    suite.addTest(unittest.makeSuite(ZODBImageTestCase))
    suite.addTest(unittest.makeSuite(BlobImageTestCase))
    suite.addTest(unittest.makeSuite(MiscellaneousImageTestCase))
    return suite
