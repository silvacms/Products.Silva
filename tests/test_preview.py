# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.tests.helpers import enablePreview, resetPreview

import SilvaTestCase


class PreviewTest(SilvaTestCase.SilvaFunctionalTestCase):


    def afterSetUp(self):
        """Create some contents for testing:

        root
        |-- doc
        `-- doc2
        """

        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        self.doc2 = self.add_document(self.root, 'doc2', u'Test Document 2')

    def test_preview(self):
        pass


import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PreviewTest))
    return suite

