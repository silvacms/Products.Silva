#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Interface.Implements import implements
from Products.Silva.transform.interfaces import IRendererRegistry
from Products.Silva.transform.RendererRegistry import RendererRegistry
from Products.Silva.tests.testrenderers.HelloWorldRenderer import HelloWorldRenderer
from Products.Silva.tests.testrenderers.UpperCaseAllRenderer import UpperCaseAllRenderer

class MockRendererRegistry(RendererRegistry):

    def __init__(self):
        self._registry = {
            'Silva Document' : [HelloWorldRenderer(), UpperCaseAllRenderer()]}

class RendererRegistryTest(SilvaTestCase.SilvaTestCase):

    def test_implements_renderer_interface(self):
        IRendererRegistry.isImplementedByInstancesOf(RendererRegistry)
        implements(RendererRegistry, IRendererRegistry)

    def test_get_renderers_for_meta_type(self):
        rr = MockRendererRegistry()
        sd_renderers = rr.getRenderersForMetaType("Silva Document")
        self.assertEquals(len(sd_renderers), 2)
        self.assert_(isinstance(sd_renderers[0], HelloWorldRenderer))
        self.assert_(isinstance(sd_renderers[1], UpperCaseAllRenderer))

    def test_get_renderer_by_id(self):
        rr = MockRendererRegistry()
        self.assert_(isinstance(
            rr.getRendererById(
                renderer_id = 'HelloWorldRenderer', meta_type = 'Silva Document'),
            HelloWorldRenderer))

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SilvaObjectTestCase))
        return suite
