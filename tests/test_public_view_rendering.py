#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from zope.interface import implements
from DateTime import DateTime
from Products.Silva.silvaxml import xmlimport
from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.transform.rendererreg import getRendererRegistry

expected_html = '<table><tr>\n<td valign="top">\n<h2 class="heading">This is a rendering test</h2>\n<p class="p">This is a test of the XSLT rendering functionality.</p>\n</td>\n<td valign="top"></td>\n</tr></table>\n'
expected_html2 = '<h2 class="heading">This is a rendering test</h2>\n\n<p class="p">This is a test of the XSLT rendering functionality.</p>\n\n\n               \n\n'

class FakeRenderer:

    implements(IRenderer)

    def render(self, version):
        return "I faked all my renderings."
        
    def getName(self):
        return "Fake Renderer"

def testopen(path, rw='r'):
    directory = os.path.dirname(__file__)
    return open(os.path.join(directory, path), rw)
    
class PublicViewRenderingTest(SilvaTestCase.SilvaTestCase):

    def afterSetUp(self):
        self._xslt = True
        try: 	 
            import libxslt
        except ImportError: 	
            self._xslt = False
            return
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is a testfolder',
            policy_name='Silva AutoTOC')
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = testopen("data/test_document.xml")
        importer.importFromFile(
            source_file, result = importfolder,
            settings = test_settings, info = test_info)
        source_file.close()
        
    def test_render_preview(self):
        if not self._xslt:
            return
        obj = self.root.silva_xslt.test_document
        obj.set_renderer_name('Images on Right')
        self.assertEqual(obj.preview(), expected_html)

    def test_render_public_view(self):
        if not self._xslt:
            return
        obj = self.root.silva_xslt.test_document
        obj.set_renderer_name('Images on Right')
        self.assertEqual(str(obj.view())[:8], "<p>Sorry")
        obj.set_unapproved_version_publication_datetime(DateTime())
        obj.approve_version()
        self.assertEqual(obj.view(), expected_html)

    def test_default_renderer(self):
        if not self._xslt:
            return
        registry_service = self.root.service_renderer_registry
        obj = self.root.silva_xslt.test_document
        obj.set_renderer_name(None)
        self.assertEqual(obj.preview().strip(), expected_html2.strip())
        registry_service.registerDefaultRenderer('Silva Document', 'Images on Right')
        self.assertEqual(obj.preview(), expected_html)
        registry_service.registerDefaultRenderer('Silva Document', None)

    def test_add_renderer(self):
        if not self._xslt:
            return
        registry_service = self.root.service_renderer_registry
        obj = self.root.silva_xslt.test_document
        registry = getRendererRegistry()
        registry.registerRenderer(
            'Silva Document',
            'Fake Renderer',
            FakeRenderer())
        obj.set_renderer_name('Fake Renderer')
        self.assertEqual(obj.preview(), 'I faked all my renderings.')
        registry.unregisterRenderer('Silva Document', 'Fake Renderer')
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(PublicViewRenderingTest))
        return suite
