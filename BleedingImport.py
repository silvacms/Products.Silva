import os.path

import xml.sax
from xml.sax.handler import feature_namespaces

from Products.Silva.silvaxml import silva_import
from Products.Silva.silvaxml.xmlimport import SaxImportHandler

def bleeding_import(self):
    silva_import.initializeElementRegistry()
    silva_xml_source_file = open("/Users/bradb/Desktop/test_OOo_pub.slv")
    handler = SaxImportHandler(self.sandbox)
    parser = xml.sax.make_parser()
    parser.setFeature(feature_namespaces, 1)
    parser.setContentHandler(handler)
    parser.parse(silva_xml_source_file)
    silva_xml_source_file.close()
