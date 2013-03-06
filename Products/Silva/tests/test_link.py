# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core import interfaces
from zope.interface.verify import verifyObject

from Acquisition import aq_chain
from Products.Silva.testing import FunctionalLayer, assertTriggersEvents


class LinkTestCase(unittest.TestCase):
    """Test Silva links.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

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

        interfaces.IPublicationWorkflow(self.root.infrae).publish()
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
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addLink(
            'infrae', 'Infrae', relative=True, target=self.root.test)

        interfaces.IPublicationWorkflow(self.root.infrae).publish()
        link = self.root.infrae.get_viewable()
        self.assertEqual(link.get_target(), self.root.test)
        self.assertEqual(
            aq_chain(link.get_target()),
            aq_chain(self.root.test))
        self.assertEqual(link.get_relative(), True)

        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        self.assertEqual(browser.open('/root/infrae'), 302)
        self.assertTrue('Location' in browser.headers)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/test')

        # If we move the document around, the link will still work
        token = self.root.manage_cutObjects(['test'])
        self.root.folder.manage_pasteObjects(token)

        self.assertEqual(browser.open('/root/infrae'), 302)
        self.assertTrue('Location' in browser.headers)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/folder/test')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkTestCase))
    return suite
