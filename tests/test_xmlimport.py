# -*- coding: utf-8 -*-
import os, sys
import xml.sax
from xml.sax.handler import feature_namespaces
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva import mangle
from Products.SilvaMetadata.Compatibility import getToolByName
from Products.Silva.silvaxml import silva_import
from Products.Silva.silvaxml.xmlimport import SaxImportHandler

class SetTestCase(SilvaTestCase.SilvaTestCase):
    def test_folder_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        silva_import.initializeElementRegistry()
        source_file = open('data/test_folder.xml', 'r')
        handler = SaxImportHandler(importfolder)
        parser = xml.sax.make_parser()
        parser.setFeature(feature_namespaces, 1)
        parser.setContentHandler(handler)
        parser.parse(source_file)
        source_file.close()
        
    def test_document_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        silva_import.initializeElementRegistry()
        source_file = open('data/test_document.xml', 'r')
        handler = SaxImportHandler(importfolder)
        parser = xml.sax.make_parser()
        parser.setFeature(feature_namespaces, 1)
        parser.setContentHandler(handler)
        parser.parse(source_file)
        source_file.close()
        document_version = importfolder.testfolder.test_document.get_editable()
        self.assertEquals(
            document_version.get_title(),
            'This is (surprise!) a document'
            )
        metadata_service = getToolByName(document_version, 'portal_metadata')
        binding = metadata_service.getMetadata(document_version)
        self.assertEquals(
            binding._getData('silva-extra').data['location'],
            'http://nohost/root/testfolder/test_document')
        doc = document_version.content.documentElement.__str__()
        self.assertEquals(doc,
        u'<doc>\n            <p>\n            <em>\u627f\u8afe\u5e83\u544a\uff0a\u65e2\u306b\u3001\uff12\u5104\u3001\uff13\u5104\u3001\uff15\u5104\uff19\u5343\u4e07\u5186\u53ce\u5165\u8005\u304c\u7d9a\u51fa<strong>boo</strong>\n              baz</em>\n            </p>\n          </doc>')
        
    def test_link_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        silva_import.initializeElementRegistry()
        source_file = open('data/test_link.xml', 'r')
        handler = SaxImportHandler(importfolder)
        parser = xml.sax.make_parser()
        parser.setFeature(feature_namespaces, 1)
        parser.setContentHandler(handler)
        parser.parse(source_file)
        source_file.close()
        linkversion = importfolder.testfolder.testfolder2.test_link.get_editable()
        self.assertEquals(
            linkversion.get_title(),
            'This is a test link, you insensitive clod!'
            )
        metadata_service = getToolByName(linkversion, 'portal_metadata')
        binding = metadata_service.getMetadata(linkversion)
        self.assertEquals(
            binding._getData('silva-extra').data['creator'],
            'test_user_1_')

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite    