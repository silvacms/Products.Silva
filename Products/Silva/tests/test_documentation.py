# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from zope.interface.verify import verifyObject

from silva.core.interfaces import IPublication
from Products.Silva.testing import FunctionalLayer, TestRequest
from Products.Silva.ExtensionService import install_documentation


class DocumentationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('chiefeditor')

    def test_install_documentation(self):
        """Test documentation installation. That should not make any
        error at all.
        """
        self.assertFalse('docs' in self.root.objectIds())

        install_documentation(self.root, TestRequest())
        self.assertTrue('docs' in self.root.objectIds())
        self.assertTrue(verifyObject(IPublication, self.root._getOb('docs')))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentationTestCase))
    return suite
