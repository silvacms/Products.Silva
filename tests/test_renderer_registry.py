#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.Silva.transform.interfaces import IRendererRegistry
from Products.Silva.RendererRegistryService import RendererRegistryService
from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer

class RendererRegistryTest(SilvaTestCase.SilvaTestCase):

    def test_renderers_registered_for_meta_type(self):
        registry_service = self.root.service_renderer_registry
        doc_version_renderers = registry_service.getRendererNamesForMetaType("Silva Document")
        self.assertEquals(len(doc_version_renderers), 2)
        self.assertEquals(registry_service.getRendererNamesForMetaType("NotReal"), [])

    def test_get_renderer_by_name(self):
        registry_service = self.root.service_renderer_registry
        self.assert_(
            isinstance(
                registry_service.getRenderer(
                    'Silva Document',
                    'Images on Right'
                    ),
                ImagesOnRightRenderer))

    def test_get_default_renderer_name_for_meta_type(self):
        registry_service = self.root.service_renderer_registry
        self.assertEqual(
            registry_service.getDefaultRendererNameForMetaType("Silva Document"),
            None)
        self.assertEqual(
            registry_service.getDefaultRendererNameForMetaType("Foobar"),
            None)
        registry_service.registerDefaultRenderer('Silva Document', 'Images on Right')
        self.assertEqual(
            registry_service.getDefaultRendererNameForMetaType("Silva Document"),
            'Images on Right')
        registry_service.registerDefaultRenderer('Silva Document', None)
        self.assertEqual(
            registry_service.getDefaultRendererNameForMetaType("Silva Document"),
            None)

    def test_get_registered_content_types(self):
        registry_service = self.root.service_renderer_registry
        self.assertEqual(
            registry_service.getRegisteredMetaTypes(), ['Silva Document'])
    
if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(RendererRegistryTest))
        return suite
