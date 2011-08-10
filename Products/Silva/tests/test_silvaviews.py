# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer


class SilvaViewsTraversingTestCase(unittest.TestCase):
    """Test SMI access.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_edit_index(self):
        """Access edit URL. You need to be authenticated to do
        it. There is no cache for the SMI.
        """
        browser = self.layer.get_browser()
        self.assertEqual(browser.open('/root/folder/edit'), 401)

        browser.login('editor', 'editor')
        self.assertEqual(browser.open('/root/folder/edit'), 200)

        self.assertTrue('Pragma' in browser.headers)
        self.assertTrue('Cache-Control' in browser.headers)
        self.assertEqual(browser.headers['Pragma'], 'no-cache')
        self.assertEqual(
            browser.headers['Cache-Control'],
            'no-cache, must-revalidate, post-check=0, pre-check=0')

    def test_edit_page(self):
        """Access a page in edit.
        """
        browser = self.layer.get_browser()
        self.assertEqual(browser.open('/root/folder/edit/tab_metadata'), 401)

        browser.login('editor', 'editor')
        self.assertEqual(browser.open('/root/folder/edit/tab_metadata'), 200)

        self.assertTrue('Pragma' in browser.headers)
        self.assertTrue('Cache-Control' in browser.headers)
        self.assertEqual(browser.headers['Pragma'], 'no-cache')
        self.assertEqual(
            browser.headers['Cache-Control'],
            'no-cache, must-revalidate, post-check=0, pre-check=0')

    def test_not_found_edit_page(self):
        """Try to access a non-existing page in edit.
        """
        browser = self.layer.get_browser()
        self.assertEqual(browser.open('/root/folder/edit/tab_nothing'), 404)

        browser.login('editor', 'editor')
        self.assertEqual(browser.open('/root/folder/edit/tab_nothing'), 404)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaViewsTraversingTestCase))
    return suite
