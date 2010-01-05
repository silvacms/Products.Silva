# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.tests.helpers import publishObject
from Products.Silva.tests.SilvaBrowser import SilvaBrowser
from Products.Silva.tests import SilvaTestCase

class PreviewTest(SilvaTestCase.SilvaFunctionalTestCase):


    def afterSetUp(self):
        """Create some contents for testing:

        root
        |-- doc
        `-- doc2
        """

        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        publishObject(self.doc)
        self.doc2 = self.add_document(self.root, 'doc2', u'Test Second Document')

    def test_preview(self):
        browser = SilvaBrowser()
        # Look at the front page. We should not see the unpublish document.
        code, url = browser.go('http://localhost/root')
        self.assertEqual(200, code)
        self.failUnless('Test Document' in browser.contents)
        self.failIf('Test Second Document' in browser.contents)
        link_doc = browser.get_href_named('Test Document')
        self.assertEqual(link_doc.url, 'http://localhost/root/doc')

        # In preview, we should be logged
        code, url = browser.go('http://localhost/root/++preview++')
        self.assertEqual(401, code)
        browser.login()
        code, url = browser.go('http://localhost/root/++preview++')
        self.assertEqual(200, code)
        self.failUnless('Test Document' in browser.contents)
        self.failUnless('Test Second Document' in browser.contents)

        # Link should to be rewritten using ++preview++
        link_doc = browser.get_href_named('Test Document')
        self.assertEqual(link_doc.url, 'http://localhost/root/++preview++/doc')
        link_doc2 = browser.get_href_named('Test Second Document')
        self.assertEqual(link_doc2.url, 'http://localhost/root/++preview++/doc2')

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PreviewTest))
    return suite

