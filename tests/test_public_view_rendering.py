#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from DateTime import DateTime
from Products.Silva.silvaxml import xmlimport

# XXX: does it matter that these tests are only testing
# against the actual rendering of the content of the doc
# itself (vs. say, the whole page that gets rendered when
# one asks for a public preview, with the Silva UI widgets
# rendered, etc.?)
#
# I don't see why it would, so since it's easier to test
# by avoiding that stuff, I will for now.
class PublicViewRenderingTest(SilvaTestCase.SilvaTestCase):

    def test_render_preview(self):
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
        version = obj.get_editable()
        pm = self.root.service_metadata
        silva_extra = pm.getMetadata(version)
        silva_extra.setValues("silva-extra", {'renderer_name' : "Images on Right"})

        self.assertEqual(obj.preview(), '<?xml version="1.0"?>\n<table><tr><td valign="top"><h2 class="heading">This is a rendering test</h2><p xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva="http://infrae.com/ns/silva" class="p">This is a test of the XSLT rendering functionality.</p></td><td valign="top"/></tr></table>\n')

    def test_render_public_view(self):
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
        version = obj.get_editable()
        pm = self.root.service_metadata
        silva_extra = pm.getMetadata(version)
        silva_extra.setValues("silva-extra", {'renderer_name' : "Images on Right"})

        self.assertEqual(obj.view(), "Sorry, this document is not published yet.")
        obj.set_unapproved_version_publication_datetime(DateTime())
        obj.approve_version()
        self.assertEqual(obj.view(), '<?xml version="1.0"?>\n<table><tr><td valign="top"><h2 class="heading">This is a rendering test</h2><p xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva="http://infrae.com/ns/silva" class="p">This is a test of the XSLT rendering functionality.</p></td><td valign="top"/></tr></table>\n')


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(PublicViewRenderingTest))
        return suite
