#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Interface.Verify import verifyClass
from Interface.Exceptions import BrokenImplementation, DoesNotImplement, BrokenMethodImplementation

import SilvaTestCase
from Products.Silva.silvaxml import xmlimport
from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.transform.renderers.imagesonrightrenderer import ImagesOnRightRenderer
from Products.Silva.transform.renderers.xsltrendererbase import RenderError

class ImagesOnRightRendererTest(SilvaTestCase.SilvaTestCase):

    def test_implements_renderer_interface(self):
        images_on_right = ImagesOnRightRenderer()
        try:
            verifyClass(IRenderer, ImagesOnRightRenderer)
        except (BrokenImplementation, DoesNotImplement, BrokenMethodImplementation):
            self.fail("ImagesOnRightRenderer does not implement IRenderer")

    def test_get_renderer_name(self):
        images_on_right = ImagesOnRightRenderer()
        self.assertEquals(images_on_right.getName(), "Images on Right")

    def test_renders_images_on_right(self):
        try:
            import libxslt
        except ImportError:
            return
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = open("data/test_document2.xml")
        importer.importFromFile(
            source_file, result = importfolder,
            settings = test_settings, info = test_info)
        source_file.close()
        # XXX get a (which?) version
        obj = self.root.silva_xslt.test_document

        images_on_right = ImagesOnRightRenderer()
        self.assertEquals(images_on_right.render(obj), '<?xml version="1.0"?>\n<table><tr><td valign="top">unapproved<h2 class="heading">This is a rendering test</h2><p xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva="http://infrae.com/ns/silva" class="p">This is a test of the XSLT rendering functionality.</p></td><td valign="top"><a href="bar.html"><img src="foo"/></a><br/></td></tr></table>\n')

    def test_error_handling(self):
        try:
            import libxslt
        except ImportError:
            return

        class BrokenImagesOnRightRenderer(ImagesOnRightRenderer):
            def __init__(self):
                ImagesOnRightRenderer.__init__(self)
                self._stylesheet_path = "data/images_to_the_right_broken.xslt"

        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = open("data/test_document2.xml")
        importer.importFromFile(
            source_file, result = importfolder,
            settings = test_settings, info = test_info)
        source_file.close()
        # XXX get a (which?) version
        obj = self.root.silva_xslt.test_document

        images_on_right = BrokenImagesOnRightRenderer()
        self.assertRaises(RenderError, images_on_right.render, obj)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ImagesOnRightRendererTest))
        return suite
