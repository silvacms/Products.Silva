import os.path

import xml.sax
from xml.sax.handler import feature_namespaces

from Products.Silva.silvaxml import xmlimport

def bleeding_import(self):
    xmlimport.initializeXMLImportRegistry()
    xmlimport.importer = theXMLImporter
    silva_xml_source_file = open("/Users/bradb/Desktop/test_OOo_pub.slv")
    importer.importFromFile(silva_xml_source_file, self.sandbox)
    silva_xml_source_file.close()
