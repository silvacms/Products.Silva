# -*- coding: utf-8 -*-
import os, sys
import xml.sax
from xml.sax.handler import feature_namespaces
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva import mangle
from Products.Silva.silvaxml import xmlimport 

class SetTestCase(SilvaTestCase.SilvaTestCase):
    def test_folder_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        importer = xmlimport.theXMLImporter
        source_file = open('data/test_folder.xml', 'r')
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        importer.importFromFile(
            source_file,
            result=importfolder,
            settings=test_settings,
            info=test_info)
        source_file.close()
        folder = importfolder.testfolder.testfolder2
        self.assertEquals(
            folder.get_title(),
            u'another; testfolder'
            )
        
    def test_link_import(self):
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        importer = xmlimport.theXMLImporter
        source_file = open('data/test_link.xml', 'r')
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        importer.importFromFile(
            source_file,
            result=importfolder,
            settings=test_settings,
            info=test_info)
        source_file.close()
        linkversion = importfolder.testfolder.testfolder2.test_link.get_editable()
        linkversion2 = importfolder.testfolder.testfolder2.test_link.get_previewable()
        self.assertEquals(
            linkversion.get_title(),
            'approved title'
            )
        metadata_service = linkversion.service_metadata
        binding = metadata_service.getMetadata(linkversion)
        self.assertEquals(
            binding._getData(
                'silva-extra').data['creator'],
                'test_user_1_')

    def test_zip_import(self):
        from StringIO import StringIO
        from zipfile import ZipFile
        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        importer = xmlimport.theXMLImporter
        zip_file = ZipFile('data/test_export.zip', 'r')
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        test_info.setZipFile(zip_file)
        bytes = zip_file.read('silva.xml')
        source_file = StringIO(bytes)
        importer.importFromFile(
            source_file,
            result=importfolder,
            settings=test_settings,
            info=test_info)
        source_file.close()
        zip_file.close()
        # normal xml import works
        self.assertEquals(
            importfolder.testfolder.testfolder2.test_link.id,
            'test_link')
        # asset file import works
        self.assertEquals(
            importfolder.testfolder.testfolder2['testzip']['sound1.mp3'].id,
            'sound1.mp3')
        # .zexp import works:
        self.assertEquals(
            importfolder.testfolder.testfolder2.testzip.foo.bar.baz['image5.jpg'].id,
            'image5.jpg')
            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite    
