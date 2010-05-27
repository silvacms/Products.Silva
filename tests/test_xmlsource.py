# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re
import unittest

from Products.Silva.tests import SilvaTestCase, helpers
from Products.Silva.silvaxml import xmlimport, xmlexport
from Products.Silva.transform.interfaces import IXMLSource

DATETIME_RE = re.compile(
    r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')


class XMLSourceTest(SilvaTestCase.SilvaTestCase):
    """Test XML source adapter.
    """

    def genericize(self, string):
        return DATETIME_RE.sub(r'YYYY-MM-DDTHH:MM:SS', string)

    def test_xml_source(self):
        importfolder = self.add_folder(
            self.root,
            'silva_xslt',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        importer = xmlimport.theXMLImporter
        test_settings = xmlimport.ImportSettings()
        test_info = xmlimport.ImportInfo()
        source_file = helpers.openTestFile("test_document.xml")
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
            IXMLSource(obj).getXML()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLSourceTest))
    return suite
