#!/usr/bin/python

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.Silva.silvaxml import xmlimport, xmlexport
from Products.Silva.adapters import xmlsource

class XMLSourceTest(SilvaTestCase.SilvaTestCase):

    def test_xml_source(self):
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

        # XXX: this way test of testing the XML output sucks but with
        # a hard deadline in place, things have to keep moving.  in an
        # ideal world, the output compared against would be a string
        # literal, of course.
        obj = self.root.silva_xslt.test_document
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(obj)
        expected_xml = exporter.exportToString(exportRoot, settings)
        self.assertEqual(
            xmlsource.XMLSourceAdapter(obj).getXML(), expected_xml)

if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SilvaObjectTestCase))
        return suite
