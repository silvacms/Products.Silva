# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core import interfaces
from zope.interface.verify import verifyObject

from Acquisition import aq_chain
from Products.Silva.testing import FunctionalLayer, assertTriggersEvents
from Products.Silva.tests.helpers import publish_object


class LinkTestCase(unittest.TestCase):
    """Test Silva links.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def test_link(self):
        """Test that link triggers events.
        """
        factory = self.root.manage_addProduct['Silva']
        with assertTriggersEvents('ObjectCreatedEvent'):
            factory.manage_addLink('link', 'Link')

        link = self.root.link
        self.failUnless(verifyObject(interfaces.ILink, link))

    def test_link_absolute(self):
        """Test absolute links.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addLink(
            'infrae', 'Infrae', relative=False, url='http://infrae.com')

        publish_object(self.root.infrae)
        link = self.root.infrae.get_viewable()
        self.assertEqual(link.get_url(), 'http://infrae.com')
        self.assertEqual(link.get_relative(), False)

        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        self.assertEqual(browser.open('/root/infrae'), 302)
        self.assertTrue('Location' in browser.headers)
        self.assertEqual(
            browser.headers['Location'],
            'http://infrae.com')

    def test_link_relative(self):
        """Test absolute links.
        """
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addLink(
            'infrae', 'Infrae', relative=True, target=self.root.document)

        publish_object(self.root.infrae)
        link = self.root.infrae.get_viewable()
        self.assertEqual(link.get_target(), self.root.document)
        self.assertEqual(
            aq_chain(link.get_target()),
            aq_chain(self.root.document))
        self.assertEqual(link.get_relative(), True)

        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        self.assertEqual(browser.open('/root/infrae'), 302)
        self.assertTrue('Location' in browser.headers)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/document')

        # If we move the document around, the link will still work
        token = self.root.manage_cutObjects(['document'])
        self.root.folder.manage_pasteObjects(token)

        self.assertEqual(browser.open('/root/infrae'), 302)
        self.assertTrue('Location' in browser.headers)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/folder/document')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkTestCase, 'test'))
    return suite
