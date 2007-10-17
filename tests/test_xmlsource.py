import os, re
import SilvaTestCase
from Products.Silva.silvaxml import xmlimport, xmlexport
from Products.Silva.adapters import xmlsource

class XMLSourceTest(SilvaTestCase.SilvaTestCase):
    DATETIME_RE = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
    def replace_datetimes(self, s):
        return self.DATETIME_RE.sub(r'YYYY-MM-DDTHH:MM:SS', s)

    def genericize(self, s):
        return self.replace_datetimes(s)

    def test_xml_source(self):
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        xmlimport.initializeXMLImportRegistry()
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        directory = os.path.dirname(__file__)
        source_file = open(os.path.join(directory, "data/test_document.xml"))
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
        expected_xml = self.genericize(
            exporter.exportToString(exportRoot, settings))
        self.assertEqual(
            expected_xml, self.genericize(
            xmlsource.XMLSourceAdapter(obj).getXML()))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLSourceTest))
    return suite
