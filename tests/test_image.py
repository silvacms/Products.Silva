# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: test_image.py,v 1.1.2.2 2004/07/12 11:49:49 guido Exp $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


import SilvaTestCase


from StringIO import StringIO
import PIL

from Products.Silva import Image

from test_file import FileTest

class ImageTest(SilvaTestCase.SilvaTestCase):
   
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
        
    
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(FileTest))
        return suite
