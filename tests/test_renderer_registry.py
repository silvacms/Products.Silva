#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.Silva.transform.interfaces import IRendererRegistry
from Products.Silva.RendererRegistryService import RendererRegistryService, OLD_STYLE_RENDERER
xslt = True
try: 	 
    from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer
except ImportError: 	
    print 'Error importing Silva renderers'
    xslt = False

class RendererRegistryTest(SilvaTestCase.SilvaTestCase):

    def test_renderers_registered_for_meta_type(self):
        if not xslt:
            return
        registry_service = self.root.service_renderer_registry
        doc_version_renderers = registry_service.getRendererNamesForMetaType(
            "Silva Document")
        self.assertEquals(4, len(doc_version_renderers))
        self.assertEquals(
            [],
            registry_service.getRendererNamesForMetaType("NotReal"))

    def test_get_renderer_by_name(self):
        if not xslt:
            return
        registry_service = self.root.service_renderer_registry
        self.assert_(
            isinstance(
                registry_service.getRenderer(
                    'Silva Document',
                    'Images on Right'
                    ),
                ImagesOnRightRenderer))

    def test_get_default_renderer_name_for_meta_type(self):
        if not xslt:
            return
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
        if not xslt:
            return
        registry_service = self.root.service_renderer_registry
        self.assertEqual(
            registry_service.getRegisteredMetaTypes(), ['Silva Document'])

    def test_getFormRenderersList(self):
        if not xslt:
            return
        reg = self.root.service_renderer_registry
        self.assertEquals(
            ['(Default)',
             OLD_STYLE_RENDERER,
             'Basic XSLT Renderer',
             'Images on Right',
             'Without Title Renderer (Same as basic but without the document title)'],
            reg.getFormRenderersList('Silva Document'))

    def test_getRendererNamesForMetaType(self):
        if not xslt:
            return
        reg = self.root.service_renderer_registry
        self.assertEquals(
            [OLD_STYLE_RENDERER,
             'Basic XSLT Renderer',
             'Images on Right',
             'Without Title Renderer (Same as basic but without the document title)'],
            reg.getRendererNamesForMetaType('Silva Document'))
        
    def test_doesRendererExistForMetaType(self):
        if not xslt:
            return
        reg = self.root.service_renderer_registry
        self.assert_(reg.doesRendererExistForMetaType(
            'Silva Document', 'Basic XSLT Renderer'))
        self.assert_(reg.doesRendererExistForMetaType(
            'Silva Document', OLD_STYLE_RENDERER))
        self.assert_(not reg.doesRendererExistForMetaType(
            'Silva Document', 'Imaginary Renderer'))
        self.assert_(not reg.doesRendererExistForMetaType(
            'Imaginary Object', OLD_STYLE_RENDERER))
        self.assert_(not reg.doesRendererExistForMetaType(
            'Imiginary Object', 'Imaginary Renderer'))

    def test_getRenderer_without_default(self):
        if not xslt:
            return
        # first without registered default
        reg = self.root.service_renderer_registry
        # we expect None if we ask for the old-style renderer
        self.assertEquals(
            None,
            reg.getRenderer('Silva Document', OLD_STYLE_RENDERER))
        # we expect None if we ask for default
        self.assertEquals(
            None,
            reg.getRenderer('Silva Document', None))
        # we expect a renderer if we ask for one
        self.assert_(reg.getRenderer('Silva Document', 'Basic XSLT Renderer'))
        # we expect None if we ask for a non-existent renderer
        self.assertEquals(
            None,
            reg.getRenderer('Silva Document', 'Foo bar'))

    def test_getRenderer_with_default(self):
        if not xslt:
            return
        # now test with registered default
        reg = self.root.service_renderer_registry
        reg.registerDefaultRenderer('Silva Document', 'Basic XSLT Renderer')
        # we expect None if we ask for the old-style renderer
        self.assertEquals(
            None,
            reg.getRenderer('Silva Document', OLD_STYLE_RENDERER))
        # we expect a renderer if we ask for default
        self.assert_(reg.getRenderer('Silva Document', None))
        # we expect a renderer if we ask for one
        self.assert_(reg.getRenderer('Silva Document', 'Basic XSLT Renderer'))
        # we expect None if we ask for a non-existent renderer
        self.assertEquals(
            None,
            reg.getRenderer('Silva Document', 'Foo bar'))
        

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
