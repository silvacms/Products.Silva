import SilvaTestCase
from Products.Silva.silvaxml import xmlimport, xmlexport
from Products.Silva.adapters import xmlsource

class XMLSourceTest(SilvaTestCase.SilvaTestCase):

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
        # XXX: Not only does it suck, but it fails in a very small number
        # of cases: If the second changes between the exportToString and
        # the getXML, the expected_xml != the output of the getXML. 
        # AIEIEIEIIIEIIEIEEE!
        obj = self.root.silva_xslt.test_document
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(obj)
        expected_xml = exporter.exportToString(exportRoot, settings)
        self.assertEqual(
            expected_xml, xmlsource.XMLSourceAdapter(obj).getXML())

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLSourceTest))
    return suite
