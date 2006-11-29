import os
from zope.interface.verify import verifyClass
from zope.interface.exceptions import BrokenImplementation, DoesNotImplement,\
     BrokenMethodImplementation
import SilvaTestCase
from Products.Silva.silvaxml import xmlimport
from Products.Silva.transform.interfaces import IRenderer
xslt = True
try: 	 
    from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer
    from Products.Silva.transform.renderer.xsltrendererbase import RenderError
except ImportError: 	
    xslt = False

directory = os.path.dirname(__file__)
expected_html = '<table>\n  <tr>\n    <td valign="top" rowspan="1" colspan="1">\n      <h2 class="heading">This is a rendering test</h2>\n      <p class="p">This is a test of the XSLT rendering functionality.</p>\n    </td>\n    <td valign="top" rowspan="1" colspan="1">\n      <a href="http://nohost/root/silva_xslt/bar.html" shape="rect">\n        <img src="http://nohost/root/silva_xslt/foo"/>\n      </a>\n      <br clear="none"/>\n    </td>\n  </tr>\n</table>\n'

class ImagesOnRightRendererTest(SilvaTestCase.SilvaTestCase):

    def test_implements_renderer_interface(self):
        if not xslt:
            return
        images_on_right = ImagesOnRightRenderer()
        try:
            verifyClass(IRenderer, ImagesOnRightRenderer)
        except (BrokenImplementation, DoesNotImplement,
                BrokenMethodImplementation):
            self.fail("ImagesOnRightRenderer does not implement IRenderer")

    def test_renders_images_on_right(self):
        if not xslt:
            return
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is a testfolder',
            policy_name='Silva AutoTOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = open(os.path.join(directory, "data/test_document2.xml"))
        importer.importFromFile(
            source_file, result = importfolder,
            settings = test_settings, info = test_info)
        source_file.close()
        # XXX get a (which?) version
        obj = self.root.silva_xslt.test_document

        images_on_right = ImagesOnRightRenderer()
        self.assertEquals(images_on_right.render(obj), expected_html)
                                                       
    def test_error_handling(self):
        
        if not xslt:
            return

        class BrokenImagesOnRightRenderer(ImagesOnRightRenderer):
            def __init__(self):
                ImagesOnRightRenderer.__init__(self)
                self._stylesheet_path = os.path.join(
                    directory,
                    "data/images_to_the_right_broken.xslt")

        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is a testfolder',
            policy_name='Silva AutoTOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = open(os.path.join(directory, "data/test_document2.xml"))
        importer.importFromFile(
            source_file, result = importfolder,
            settings = test_settings, info = test_info)
        source_file.close()
        # XXX get a (which?) version
        obj = self.root.silva_xslt.test_document

        images_on_right = BrokenImagesOnRightRenderer()
        self.assertRaises(RenderError, images_on_right.render, obj)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImagesOnRightRendererTest))
    return suite
