# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, http

AUTH={'Authorization': 'Basic editor:editor'}


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
        response = http(
            'GET /root/folder/edit HTTP/1.0', parsed=True)
        self.assertEqual(response.getStatus(), 401)

        response = http(
            'GET /root/folder/edit HTTP/1.0', headers=AUTH, parsed=True)
        self.assertEqual(response.getStatus(), 200)

        headers = response.getHeaders()
        self.failUnless('Pragma' in headers)
        self.failUnless('Cache-Control' in headers)
        self.assertEqual(headers['Pragma'], 'no-cache')
        self.assertEqual(
            headers['Cache-Control'],
            'post-check=0, pre-check=0')

    def test_edit_page(self):
        """Access a page in edit.
        """
        response = http(
            'GET /root/folder/edit/tab_metadata HTTP/1.0',
            parsed=True)
        self.assertEqual(response.getStatus(), 401)

        response = http(
            'GET /root/folder/edit/tab_metadata HTTP/1.0',
            headers=AUTH, parsed=True)
        self.assertEqual(response.getStatus(), 200)

        headers = response.getHeaders()
        self.failUnless('Pragma' in headers)
        self.failUnless('Cache-Control' in headers)
        self.assertEqual(headers['Pragma'], 'no-cache')
        self.assertEqual(
            headers['Cache-Control'],
            'no-cache, must-revalidate, post-check=0, pre-check=0')

    def test_not_found_edit_page(self):
        """Try to access a non-existing page in edit.
        """
        response = http(
            'GET /root/folder/edit/tab_nothing HTTP/1.0',
            parsed=True, handle_errors=True)
        self.assertEqual(response.getStatus(), 404)

        response = http(
            'GET /root/folder/edit/tab_nothing HTTP/1.0',
            headers=AUTH, parsed=True, handle_errors=True)
        self.assertEqual(response.getStatus(), 404)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaViewsTraversingTestCase))
    return suite
