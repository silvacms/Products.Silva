# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_image.py,v 1.8 2006/01/24 16:13:33 faassen Exp $
import SilvaTestCase
from Testing.ZopeTestCase.ZopeTestCase import ZopeTestCase
from Testing.ZopeTestCase import utils


from StringIO import StringIO

try:
    import PIL
except ImportError:
    havePIL = 0
else:
    havePIL = 1

from Products.Silva import Image

from test_file import FileTest

class ImageTest(SilvaTestCase.SilvaTestCase):

    def _app(self):
        app = ZopeTestCase._app(self)
        app = app.aq_base
        request_out = self.request_out = StringIO()
        return utils.makerequest(app, request_out)
   
    def test_imageformat(self):
        image_file = StringIO('invalid-image-format')
        
        self.assertRaises(ValueError, self.root.manage_addProduct['Silva'].\
            manage_addImage, 'testimage', 'Test Image', image_file)
    
    def _getimage_test(self):
        image_file = open('test_image_data/photo.tif', 'rb')
        image_data = image_file.read()
        image_file.seek(0)
        self.root.manage_addProduct['Silva'].manage_addImage('testimage',
            'Test Image', image_file)
        image_file.close()
        image = self.root.testimage
        image.set_web_presentation_properties('JPEG', '100x100', '')
        
        self.assertRaises(ValueError, image.getImage, hires=0, webformat=0)

        if not havePIL:
            return

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
        
    
    def test_getImage_zodb(self):
        self.root.service_files.manage_filesServiceEdit('', 0, '')
        self._getimage_test()
    
    def test_getImage_extfile(self):
        self.root.service_files.manage_filesServiceEdit('', 1, '')
        self._getimage_test()

    def _test_index_html(self):
        image_file = open('test_image_data/photo.tif', 'rb')
        image_data = image_file.read()
        image_file.seek(0)
        self.root.manage_addProduct['Silva'].manage_addImage('testimage',
            'Test Image', image_file)
        image_file.close()
        image = self.root.testimage
        image.set_web_presentation_properties('JPEG', '100x100', '')
        request = self.root.REQUEST

        if not havePIL:
            return

        data = image.index_html(request)
        it = self._get_req_data(data)
        pil_image = PIL.Image.open(StringIO(it))
        self.assertEquals((100, 100), pil_image.size)
        self.assertEquals('JPEG', pil_image.format)
        
        request.QUERY_STRING = 'hires'
        data = image.index_html(request)
        it = self._get_req_data(data)
        pil_image = PIL.Image.open(StringIO(it))
        self.assertEquals((960, 1280), pil_image.size)
        self.assertEquals('TIFF', pil_image.format)
        self.assertEquals(image_data, it)
        
        request.QUERY_STRING = 'thumbnail'
        data = image.index_html(request)
        it = self._get_req_data(data)
        pil_image = PIL.Image.open(StringIO(it))
        w, h = pil_image.size
        self.assert_(w == 120 or h == 120)
        self.assertEquals('JPEG', pil_image.format)

    def test_index_html_extifile(self):
        self.root.service_files.manage_filesServiceEdit('', 1, '')
        self._test_index_html()

    def test_index_html_zodb(self):
        self.root.service_files.manage_filesServiceEdit('', 0, '')
        self._test_index_html()
        
    def _get_req_data(self, data):
        if data:
            s = data
        else:
            s = self.request_out.getvalue()
            self.request_out.seek(0)
            self.request_out.truncate()
        if s.startswith('Status: 200'):
            s = s[s.find('\n\n')+2:]
        return s

    def test_getCropBox(self):
        image_file = open('test_image_data/photo.tif', 'rb')
        image_data = image_file.read()
        image_file.seek(0)
        self.root.manage_addProduct['Silva'].manage_addImage(
            'testimage', 'Test Image', image_file)
        image_file.close()
        image = self.root.testimage
        if not havePIL:
            return
        cropbox = image.getCropBox(crop="242x379-392x479")
        self.assert_(cropbox is not None)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileTest))
    return suite
