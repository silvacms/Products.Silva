# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
from zope.interface.verify import verifyClass
from zope.interface.exceptions import BrokenImplementation, DoesNotImplement,\
     BrokenMethodImplementation
import SilvaTestCase
from Products.Silva.silvaxml import xmlimport

from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.transform.rendererreg import getRendererRegistry
from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer

from lxml import etree

directory = os.path.dirname(__file__)
expected_html = '\n<table>\n  <tr>\n    <td valign="top">\n      <h2 class="heading">This is a rendering test</h2>\n      <p class="p">This is a test of the XSLT rendering functionality.</p>\n    </td>\n    <td valign="top">\n      <a href="http://nohost/root/silva_xslt/bar.html">\n        <img src="http://nohost/root/silva_xslt/foo" />\n      </a>\n      <br />\n    </td>\n  </tr>\n</table>\n'

class ImagesOnRightRendererTest(SilvaTestCase.SilvaTestCase):

    def _get_renderer_images_on_right(self):
        registry = getRendererRegistry()
        silva_doc_renderers = registry.getRenderersForMetaType('Silva Document')
        self.failUnless(len(silva_doc_renderers) != 0)
        self.failUnless('Images on Right' in silva_doc_renderers)
        return silva_doc_renderers['Images on Right']

    def test_implements_renderer_interface(self):
        images_on_right = self._get_renderer_images_on_right()
        try:
            verifyClass(IRenderer, ImagesOnRightRenderer)
        except (BrokenImplementation, DoesNotImplement,
                BrokenMethodImplementation):
            self.fail("ImagesOnRightRenderer does not implement IRenderer")

    def test_renders_images_on_right(self):
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is a testfolder',
            policy_name='Silva AutoTOC')
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
        images_on_right = self._get_renderer_images_on_right()
        self.assertEquals(images_on_right.render(obj), expected_html)
                                                       
    def test_error_handling(self):
        
        class BrokenImagesOnRightRenderer(ImagesOnRightRenderer):
            def __init__(self):
                super(BrokenImagesOnRightRenderer, self).__init__('data/images_to_the_right_broken.xslt', __file__)

        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is a testfolder',
            policy_name='Silva AutoTOC')
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
        self.assertRaises(etree.XMLSyntaxError, images_on_right.render, obj)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ImagesOnRightRendererTest))
    return suite
