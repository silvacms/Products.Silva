#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Interface.Verify import verifyClass
from Products.Silva.transform.interfaces import IRendererRegistry
from Products.Silva.transform.RendererRegistry import RendererRegistry
from Products.Silva.transform.renderers.RenderImagesOnRight import RenderImagesOnRight
from Interface.Exceptions import BrokenImplementation, DoesNotImplement, BrokenMethodImplementation

class RendererRegistryTest(SilvaTestCase.SilvaTestCase):

    def test_implements_renderer_interface(self):
        try:
            verifyClass(IRendererRegistry, RendererRegistry)
        except (BrokenImplementation, DoesNotImplement, BrokenMethodImplementation), err:
            self.fail(
                "RendererRegistry does not implement IRendererRegistry: %s" %
                str(err))

    def test_renderers_registered_for_meta_type(self):
        registry = RendererRegistry()
        doc_version_renderers = registry.getRenderersForMetaType("Silva Document Version")
        self.assertEquals(len(doc_version_renderers), 1)
        self.assert_(isinstance(doc_version_renderers[0], RenderImagesOnRight))

    def test_get_renderer_by_name(self):
        registry = RendererRegistry()
        self.assert_(
            isinstance(
                registry.getRendererByName(
                    name = 'Images on Right',
                    meta_type = 'Silva Document Version'),
                RenderImagesOnRight))

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
