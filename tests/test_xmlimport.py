# -*- coding: utf-8 -*-
import os, sys, re
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