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
            u'another; testfolder',
            folder.get_title())
        
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
            'approved title',
            linkversion.get_title())
        metadata_service = linkversion.service_metadata
        binding = metadata_service.getMetadata(linkversion)
        self.assertEquals(
           'test_user_1_',
            binding._getData(
                'silva-extra').data['creator'])

    def test_ghost_import(self):
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        # import the ghost
        source_file = open('data/test_link.xml', 'r')
        importer.importFromFile(
            source_file,
            result=self.root,
            settings=test_settings,
            info=test_info)
        source_file.close()

        source_file = open('data/test_ghost.xml', 'r')
        importer.importFromFile(
            source_file,
            result=self.root,
            settings=test_settings,
            info=test_info)
        source_file.close()
        version = self.root.testfolder3.caspar.get_editable()
        version2 = self.root.testfolder3.caspar.get_previewable()
        self.assertEquals(version.id, version2.id)
        self.assertEquals(
            'test_link',
            version.get_title()
            )
        self.assertEquals(
            'Silva Ghost Version',
            version.meta_type
            )

    def test_ghostfolder_import(self):
        importfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        haunted_folder = self.add_folder(
            importfolder,
            'testfolder2',
            'This is <boo>a</boo> haunted testfolder',
            policy_name='Auto TOC')
        importer = xmlimport.theXMLImporter
        # import the ghost folder
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = open('data/test_ghost_folder.xml', 'r')
        importer.importFromFile(
            source_file,
            result=self.root,
            settings=test_settings,
            info=test_info)
        source_file.close()
        version = self.root.testfolder3.caspar.get_editable()
        version2 = self.root.testfolder3.caspar.get_previewable()

        self.assertEquals(version.id, version2.id)
        self.assertEquals(
            'This is <boo>a</boo> haunted testfolder',
            version.get_title()
            )
        self.assertEquals(
            '/root/testfolder/testfolder2',
            version.get_haunted_url()
            )
        self.assertEquals(
            'Silva Ghost Folder',
            version.meta_type
            )

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
            'test_link',
            importfolder.testfolder.testfolder2.test_link.id)
        # asset file import works
        self.assertEquals(
            'sound1.wav',
            importfolder.testfolder.testfolder2['testzip']['sound1.wav'].id)
        self.assertEquals(
            'Silva File',
            importfolder.testfolder.testfolder2['testzip']['sound1.wav'].meta_type)
        # image file import works:
        self.assertEquals(
            'image5.jpg',
            importfolder.testfolder.testfolder2.testzip.foo.bar.baz['image5.jpg'].id)
        self.assertEquals(
            'Silva Image',
            importfolder.testfolder.testfolder2.testzip.foo.bar.baz['image5.jpg'].meta_type) 
        # ghost import
        self.assertEquals(
            'Silva Ghost',
            importfolder.testfolder.testfolder2['haunting_the_neighbour'].meta_type) 
        self.assertEquals(
            '/silva/silva/testfolder/testfolder2/test_link',
            importfolder.testfolder.testfolder2['haunting_the_neighbour'].get_haunted_url()) 

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite    
