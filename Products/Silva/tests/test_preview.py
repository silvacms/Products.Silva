# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow

class PreviewTestCase(unittest.TestCase):
    """Test preview access.
    """
    layer = FunctionalLayer

    def setUp(self):
        """Create some contents for testing:

        root
        |-- doc
        `-- doc2
        """
        self.root = self.layer.get_application()
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('info', u'Information')
        factory.manage_addMockupVersionedContent('contact', u'Contact')
        IPublicationWorkflow(self.root.info).publish()

    def test_preview_links(self):
        """In preview, we see not yet published content.
        """
        browser = self.layer.get_browser()

        self.assertEqual(browser.open('http://localhost/root'), 200)
        link = browser.get_link('Information')
        self.assertEqual(link.url, 'http://localhost/root/info')
        self.assertRaises(AssertionError, browser.get_link, u'Contact')

        # Access preview. We need to be reader for it.
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        browser.login('viewer', 'viewer')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 401)

        browser.login('manager', 'manager')
        self.assertEqual(browser.open('http://localhost/root/++preview++'), 200)

        # We now see both pages (unpublished as well), links are rewritten.
        link = browser.get_link('Information')
        self.assertEqual(link.url, 'http://localhost/root/++preview++/info')
        link = browser.get_link('Contact')
        self.assertEqual(link.url, 'http://localhost/root/++preview++/contact')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PreviewTestCase))
    return suite
