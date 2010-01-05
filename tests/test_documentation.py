# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import SilvaTestCase

class DocumentationTestCase(SilvaTestCase.SilvaTestCase):

    def test_install(self):
        """Test documentation installation. That should not make any
        error at all.
        """
        self.root.manage_installDocumentation()


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocumentationTestCase))
    return suite

