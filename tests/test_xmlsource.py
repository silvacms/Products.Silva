# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re
import unittest

from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter

from Products.Silva.testing import FunctionalLayer
from Products.Silva.silvaxml import xmlimport, xmlexport
from Products.Silva.transform.interfaces import IXMLSource
from Products.Silva.tests.test_xmlexport import SilvaXMLTestCase


class XMLSourceTest(SilvaXMLTestCase):
    """Test XML source adapter.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Test Document')

    def test_versioned_content(self):
        document = self.root.document
        request = TestRequest()
        source = getMultiAdapter((document, request), IXMLSource)

        self.failUnless(verifyObject(IXMLSource, source))
        self.assertExportEqual(source.getXML(), 'test_source_document.silvaxml')

    def test_version(self):
        version = self.root.document.get_editable()
        request = TestRequest()
        source = getMultiAdapter((version, request), IXMLSource)

        self.failUnless(verifyObject(IXMLSource, source))
        self.assertExportEqual(source.getXML(), 'test_source_version.silvaxml')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLSourceTest))
    return suite
