# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.ExtensionService import install_documentation
from Products.Silva.tests import SilvaTestCase


class DocumentationTestCase(SilvaTestCase.SilvaTestCase):

    def test_install(self):
        """Test documentation installation. That should not make any
        error at all.
        """
        install_documentation(self.root)
        self.failUnless(hasattr(self.root.aq_explicit, 'docs'))


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentationTestCase))
    return suite

