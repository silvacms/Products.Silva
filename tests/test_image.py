# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from StringIO import StringIO
import PIL

# Zope 3
from zope import component
from zope.interface.verify import verifyObject

from silva.core import interfaces
from Products.Silva import File, magic
from Products.Five.testbrowser import Browser
from Testing.ZopeTestCase.zopedoctest.functional import http

from Products.Silva.tests import SilvaTestCase
from Products.Silva.tests import helpers


class ImageTestHelper(object):

    def add_test_image(self):
        image_file = helpers.openTestFile('photo.tif')
        image_data = image_file.read()
        image_file.seek(0)
        self.root.manage_addProduct['Silva'].manage_addImage(
            'testimage.tif', 'Test Image', image_file)
        image_file.close()
        return getattr(self.root, 'testimage.tif'), image_data


class ImageTest(SilvaTestCase.SilvaTestCase, ImageTestHelper):

    def test_badimage(self):
        image_file = StringIO('invalid-image-format')
        self.assertRaises(ValueError, self.root.manage_addProduct['Silva'].\
            manage_addImage, 'badimage', 'Bad Image', image_file)

    def _test_image(self):
        image, image_data = self.add_test_image()

        self.failUnless(verifyObject(interfaces.IImage, image))
        self.assertEquals(image.getFormat(), 'TIFF')
        self.assertEquals(image.getDimensions(), (960, 1280))
        self.assertEquals(str(image.getOrientation()), "portrait")
        image.set_web_presentation_properties('JPEG', '100x100', '')
        self.assertRaises(ValueError, image.getImage, hires=0, webformat=0)
        self.failUnless(image.tag() is not None)

        it = image.getImage(hires=0, webformat=1)
        pil_image = PIL.Image.open(StringIO(it))
        self.assertEquals((100, 100), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

        it = image.getImage(hires=1, webformat=0)
        self.assertEquals(image_data, it)

        it = image.getImage(hires=1, webformat=1)
        pil_image = PIL.Image.open(StringIO(it))
        self.assertEquals((960, 1280), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

        assetdata = interfaces.IAssetData(image)
        self.failUnless(verifyObject(interfaces.IAssetData, assetdata))
        self.assertEquals(image_data, assetdata.getData())

    def test_image_blob(self):
        self.root.service_files.storage = File.BlobFile
        self._test_image()

    def test_image_zodb_default(self):
        if self.root.service_files.storage is None:
            self._test_image()

    def test_image_zodb(self):
        self.root.service_files.storage = File.ZODBFile
        self._test_image()

    def test_image_extfile(self):
        if File.FILESYSTEM_STORAGE_AVAILABLE:
            self.root.service_files.storage = File.FileSystemFile
            self._test_image()

    def test_getcropbox(self):
        image, _ = self.add_test_image()
        cropbox = image.getCropBox(crop="242x379-392x479")
        self.assert_(cropbox is not None)

    def test_copy_image(self):
        image, _ = self.add_test_image()
        self.root.action_copy(['testimage.tif'], self.app.REQUEST)
        # now do the paste action
        self.root.action_paste(self.app.REQUEST)


class ImageFunctionalTest(SilvaTestCase.SilvaFunctionalTestCase,
                          ImageTestHelper):

    def afterSetUp(self):
        image, image_data = self.add_test_image()
        image.set_web_presentation_properties('JPEG', '100x100', '')

    def test_view(self):
        browser = Browser()
        browser.open('http://localhost/root/testimage.tif')
        self.assertEquals(
            browser.headers['Content-Disposition'],
            'inline;filename=testimage.jpeg')
        self.assertEquals(
            browser.headers['Content-Type'],
            'image/jpeg')
        pil_image = PIL.Image.open(StringIO(browser.contents))
        self.assertEquals((100, 100), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

    def test_head_view(self):
        response = http('HEAD /root/testimage.tif HTTP/1.1')
        self.assertEquals(response.header_output.status, 200)
        headers = response.header_output.headers
        self.assertEquals(headers['Content-Length'], '0')
        self.assertEquals(headers['Content-Type'], 'image/jpeg')

    def test_hires(self):
        browser = Browser()
        browser.open('http://localhost/root/testimage.tif?hires')
        self.assertEquals(
            browser.headers['content-disposition'],
            'inline;filename=testimage.tif')

        if not magic.HAVE_MAGIC:
            # If we don't use the libmagic, we won't know the type of
            # the image.
            return

        self.assertEquals(
            browser.headers['content-type'],
            'image/tiff')

        # a Browser is not able to read all image data.

    def test_head_hires(self):
        response = http('HEAD /root/testimage.tif?hires HTTP/1.1')
        self.assertEquals(response.header_output.status, 200)
        headers = response.header_output.headers
        self.assertEquals(headers['Content-Length'], '0')

        if not magic.HAVE_MAGIC:
            # If we don't use the libmagic, we won't know the type of
            # the image.
            return

        self.assertEquals(headers['Content-Type'], 'image/tiff')

    def test_thumbnail(self):
        browser = Browser()
        browser.open('http://localhost/root/testimage.tif?thumbnail')
        self.assertEquals(
            browser.headers['content-disposition'],
            'inline;filename=testimage.jpeg')
        self.assertEquals(
            browser.headers['content-type'],
            'image/jpeg')
        pil_image = PIL.Image.open(StringIO(browser.contents))
        self.assertEquals((90, 120), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)

    def test_head_thumbnail(self):
        response = http('HEAD /root/testimage.tif?thumbnail HTTP/1.1')
        self.assertEquals(response.header_output.status, 200)
        headers = response.header_output.headers
        self.assertEquals(headers['Content-Length'], '0')
        self.assertEquals(headers['Content-Type'], 'image/jpeg')



import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImageTest))
    suite.addTest(unittest.makeSuite(ImageFunctionalTest))
    return suite
