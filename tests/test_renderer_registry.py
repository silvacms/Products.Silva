# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.RendererRegistryService import OLD_STYLE_RENDERER
from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer
from Products.Silva.testing import FunctionalLayer

class RendererRegistryTest(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.registry = self.root.service_renderer_registry

    def test_renderers_registered_for_meta_type(self):
        doc_version_renderers = self.registry.getRendererNamesForMetaType(
            "Silva Document")
        self.assertEquals(4, len(doc_version_renderers))
        self.assertEquals(
            [],
            self.registry.getRendererNamesForMetaType("NotReal"))

    def test_get_renderer_by_name(self):
        self.assert_(
            isinstance(
                self.registry.getRenderer(
                    'Silva Document',
                    'Images on Right'
                    ),
                ImagesOnRightRenderer))

    def test_get_default_renderer_name_for_meta_type(self):
        self.assertEqual(
            self.registry.getDefaultRendererNameForMetaType("Silva Document"),
            None)
        self.assertEqual(
            self.registry.getDefaultRendererNameForMetaType("Foobar"),
            None)
        self.registry.registerDefaultRenderer('Silva Document', 'Images on Right')
        self.assertEqual(
            self.registry.getDefaultRendererNameForMetaType("Silva Document"),
            'Images on Right')
        self.registry.registerDefaultRenderer('Silva Document', None)
        self.assertEqual(
            self.registry.getDefaultRendererNameForMetaType("Silva Document"),
            None)

    def test_get_registered_content_types(self):
        self.assertEqual(
            self.registry.getRegisteredMetaTypes(), ['Silva Document'])

    def test_getFormRenderersList(self):
        self.assertEquals(
            ['(Default)',
             OLD_STYLE_RENDERER,
             'Basic XSLT Renderer',
             'Images on Right',
             'Without Title Renderer (Same as basic but without the document title)'],
            self.registry.getFormRenderersList('Silva Document'))

    def test_getRendererNamesForMetaType(self):
        self.assertEquals(
            [OLD_STYLE_RENDERER,
             'Basic XSLT Renderer',
             'Images on Right',
             'Without Title Renderer (Same as basic but without the document title)'],
            self.registry.getRendererNamesForMetaType('Silva Document'))

    def test_doesRendererExistForMetaType(self):
        self.assert_(self.registry.doesRendererExistForMetaType(
            'Silva Document', 'Basic XSLT Renderer'))
        self.assert_(self.registry.doesRendererExistForMetaType(
            'Silva Document', OLD_STYLE_RENDERER))
        self.assert_(not self.registry.doesRendererExistForMetaType(
            'Silva Document', 'Imaginary Renderer'))
        self.assert_(not self.registry.doesRendererExistForMetaType(
            'Imaginary Object', OLD_STYLE_RENDERER))
        self.assert_(not self.registry.doesRendererExistForMetaType(
            'Imiginary Object', 'Imaginary Renderer'))

    def test_getRenderer_without_default(self):
        # first without registered default
        # we expect None if we ask for the old-style renderer
        self.assertEquals(
            None,
            self.registry.getRenderer('Silva Document', OLD_STYLE_RENDERER))
        # we expect None if we ask for default
        self.assertEquals(
            None,
            self.registry.getRenderer('Silva Document', None))
        # we expect a renderer if we ask for one
        self.assert_(self.registry.getRenderer('Silva Document', 'Basic XSLT Renderer'))
        # we expect None if we ask for a non-existent renderer
        self.assertEquals(
            None,
            self.registry.getRenderer('Silva Document', 'Foo bar'))

    def test_getRenderer_with_default(self):
        # now test with registered default
        self.registry.registerDefaultRenderer('Silva Document', 'Basic XSLT Renderer')
        # we expect None if we ask for the old-style renderer
        self.assertEquals(
            None,
            self.registry.getRenderer('Silva Document', OLD_STYLE_RENDERER))
        # we expect a renderer if we ask for default
        self.assert_(self.registry.getRenderer('Silva Document', None))
        # we expect a renderer if we ask for one
        self.assert_(self.registry.getRenderer('Silva Document', 'Basic XSLT Renderer'))
        # we expect None if we ask for a non-existent renderer
        self.assertEquals(
            None,
            self.registry.getRenderer('Silva Document', 'Foo bar'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RendererRegistryTest))
    return suite
