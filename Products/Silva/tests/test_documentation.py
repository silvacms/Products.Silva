# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
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
        install_documentation(self.root)
        self.failUnless('docs' in self.root.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentationTestCase))
    return suite
