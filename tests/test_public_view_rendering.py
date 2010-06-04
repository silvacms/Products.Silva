# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface import implements

from Products.Silva.tests.helpers import open_test_file, publish_object
from Products.Silva.silvaxml import xmlimport
from Products.Silva.testing import FunctionalLayer, TestCase
from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.transform.rendererreg import getRendererRegistry

expected_html = u'<table>\n  <tr>\n    <td valign="top"><h2 class="heading">This is a rendering test</h2>\n                <p class="p">This is a test of the XSLT rendering functionality.</p>\n            </td>\n    <td valign="top"></td>\n  </tr>\n</table>'
expected_html2 = u'<h2 class="heading">This is a rendering test</h2>\n                <p class="p">This is a test of the XSLT rendering functionality.</p>'


class FakeRenderer:

    implements(IRenderer)

    def transform(self, context, request):
        return "I faked all my renderings."


class PublicViewRenderingTest(TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with open_test_file("test_document.xml") as source_document:
            xmlimport.importFromFile(source_document, self.root)
        self.document = self.root.test_document
        self.registry = self.root.service_renderer_registry

    def test_render_preview(self):
        self.document.set_renderer_name('Images on Right')
        self.assertStringEqual(self.document.preview(), expected_html)

    def test_render_public_view(self):
        self.document.set_renderer_name('Images on Right')
        self.assertEqual(str(self.document.view())[:8], "<p>Sorry")
        publish_object(self.document)
        self.assertStringEqual(self.document.view(), expected_html)

    def test_default_renderer(self):
        self.document.set_renderer_name(None)
        self.assertStringEqual(self.document.preview(), expected_html2)
        self.registry.registerDefaultRenderer('Silva Document', 'Images on Right')
        self.assertStringEqual(self.document.preview(), expected_html)
        self.registry.registerDefaultRenderer('Silva Document', None)

    def test_add_renderer(self):
        registry = getRendererRegistry()
        registry.registerRenderer('Silva Document', 'Fake Renderer', FakeRenderer())
        self.document.set_renderer_name('Fake Renderer')
        self.assertEqual(self.document.preview(), 'I faked all my renderings.')
        registry.unregisterRenderer('Silva Document', 'Fake Renderer')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicViewRenderingTest))
    return suite
