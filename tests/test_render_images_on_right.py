#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Interface.Verify import verifyClass
from Interface.Exceptions import BrokenImplementation, DoesNotImplement, BrokenMethodImplementation

import SilvaTestCase
from Products.Silva.silvaxml import xmlimport
from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.transform.renderers.RenderImagesOnRight import RenderImagesOnRight

class RenderImagesOnRightTest(SilvaTestCase.SilvaTestCase):

    def test_implements_renderer_interface(self):
        images_on_right = RenderImagesOnRight()
        try:
            verifyClass(IRenderer, RenderImagesOnRight)
        except (BrokenImplementation, DoesNotImplement, BrokenMethodImplementation):
            self.fail("RenderImagesOnRight does not implement IRenderer")

    def test_get_renderer_name(self):
        images_on_right = RenderImagesOnRight()
        self.assertEquals(images_on_right.getName(), "Images on Right")

    def test_renders_images_on_right(self):
        # FIXME: this is just testing against dummy output for now
        # as what's important first off is that the overall architecture
        # works. FIX THIS TEST once the stylesheet is actually called by
        # the renderer.
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = open("data/test_document.xml")
        importer.importFromFile(
            source_file, result = importfolder,
            settings = test_settings, info = test_info)
        source_file.close()

        obj = self.root.silva_xslt.test_document

        images_on_right = RenderImagesOnRight()
        self.assertEquals(images_on_right.render(obj), "images on right")


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(RenderImagesOnRightTest))
        return suite
