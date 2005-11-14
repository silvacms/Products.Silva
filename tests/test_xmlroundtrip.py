# -*- coding: utf-8 -*-
import os, sys
import xml.sax
from xml.sax.handler import feature_namespaces
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from SilvaTestCase import transaction
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva import mangle
from Products.SilvaMetadata.Compatibility import getToolByName
from Products.Silva.silvaxml import xmlimport 

class SetTestCase(SilvaTestCase.SilvaTestCase):
    def test_xml_roundtrip(self):
        from StringIO import StringIO
        from Products.Silva.silvaxml import xmlexport
        from Products.Silva.adapters import zipfileexport
        from Products.Silva.Image import Image
        from zipfile import ZipFile, BadZipfile

        directory = os.path.dirname(__file__)

        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        zip_file = ZipFile(os.path.join(directory, 'data/test_export.zip'), 'r')
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
            importfolder.testfolder.testfolder2['testzip']['sound1.wav'].id,
            'sound1.wav')
        # .zexp import works:
        self.assertEquals(
            importfolder.testfolder.testfolder2.testzip.foo.bar.baz['image5.jpg'].id,
            'image5.jpg')
        transaction.get().commit(1)
        testfolder = importfolder.testfolder
        xmlexport.initializeXMLExportRegistry()
        settings = xmlexport.ExportSettings()
        adapter = zipfileexport.getZipfileExportAdapter(testfolder)
        result = adapter.exportToZip(testfolder, settings)
        f = open(os.path.join(directory, 'test_export.zip'), 'wb')
        f.write(result)
        f.close()
        f = open(os.path.join(directory, 'test_export.zip'), 'rb')
        zip_out = ZipFile(f, 'r')
        namelist = zip_out.namelist()
        namelist.sort()
        self.assertEquals(namelist, ['assets/1', 'assets/2', 'assets/3', 'assets/4', 'assets/5', 'assets/6', 'silva.xml'])
        zip_out.close()
        f.close()
        os.remove(os.path.join(directory, 'test_export.zip'))
            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite    
