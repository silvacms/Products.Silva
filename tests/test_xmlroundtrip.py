# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
from zope.component import getAdapter

import SilvaTestCase
from SilvaTestCase import transaction
from Products.Silva.silvaxml import xmlimport
from Products.Silva import interfaces

class SetTestCase(SilvaTestCase.SilvaTestCase):
    def test_xml_roundtrip(self):
        from StringIO import StringIO
        from Products.Silva.silvaxml import xmlexport
        from zipfile import ZipFile

        directory = os.path.dirname(__file__)

        importfolder = self.add_folder(
            self.root,
            'importfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
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
        transaction.savepoint()
        testfolder = importfolder.testfolder
        xmlexport.initializeXMLExportRegistry()
        settings = xmlexport.ExportSettings()
        adapter = getAdapter(testfolder, interfaces.IContentExporter, name='zip')
        result = adapter.export(settings)
        f = open(os.path.join(directory, 'test_export.zip'), 'wb')
        f.write(result)
        f.close()
        f = open(os.path.join(directory, 'test_export.zip'), 'rb')
        zip_out = ZipFile(f, 'r')
        namelist = zip_out.namelist()
        namelist.sort()
        self.assertEquals(namelist, [
            'assets/1.jpg', 'assets/2.jpg', 'assets/3.jpg', 'assets/4.jpg',
            'assets/5.jpg', 'assets/6.wav', 'silva.xml'])
        zip_out.close()
        f.close()
        os.remove(os.path.join(directory, 'test_export.zip'))
            
import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SetTestCase))
    return suite    
