# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import ILink, ILinkVersion, IPublicationWorkflow
from silva.core.references.interfaces import IReferenceService
from zope.interface.verify import verifyObject
from zope.component import getUtility

from Acquisition import aq_chain
from Products.Silva.testing import FunctionalLayer, assertTriggersEvents
from Products.Silva.ftesting import public_settings


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
        self.assertTrue(verifyObject(ILink, link))
        editable = link.get_editable()
        self.assertTrue(verifyObject(ILinkVersion, editable))

    def test_absolute_link(self):
        """Test creating and access an absolute link that point to
        user specified URL.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addLink(
            'infrae', 'Infrae', relative=False, url='http://infrae.com')

        IPublicationWorkflow(self.root.infrae).publish()
        link = self.root.infrae.get_viewable()
        self.assertEqual(link.get_url(), 'http://infrae.com')
        self.assertEqual(link.get_relative(), False)
        self.assertEqual(link.get_target(), None)
        reference = getUtility(IReferenceService).get_reference(
            link, name=u"link")
        self.assertEqual(reference, None)

        with self.layer.get_browser() as browser:
            browser.options.follow_redirect = False
            self.assertEqual(browser.open('/root/infrae'), 302)
            self.assertTrue('Location' in browser.headers)
            self.assertEqual(
                browser.headers['Location'],
                'http://infrae.com')

    def test_relative_link(self):
        """Test creating and accessing a relative link to an another
        content in Silva.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addLink(
            'infrae', 'Infrae', relative=True, target=self.root.test)

        IPublicationWorkflow(self.root.infrae).publish()
        link = self.root.infrae.get_viewable()
        self.assertEqual(link.get_relative(), True)
        self.assertEqual(link.get_target(), self.root.test)
        self.assertEqual(
            aq_chain(link.get_target()),
            aq_chain(self.root.test))
        reference = getUtility(IReferenceService).get_reference(
            link, name=u"link")
        self.assertNotEqual(reference, None)
        self.assertEqual(reference.target, self.root.test)

        with self.layer.get_browser() as browser:
            browser.options.follow_redirect = False
            self.assertEqual(browser.open('/root/infrae'), 302)
            self.assertTrue('Last-Modified' in browser.headers)
            self.assertTrue('Location' in browser.headers)
            self.assertEqual(
                browser.headers['Location'],
                'http://localhost/root/test')

        # If we move the document around, the link will still work
        token = self.root.manage_cutObjects(['test'])
        self.root.folder.manage_pasteObjects(token)

        with self.layer.get_browser() as browser:
            browser.options.follow_redirect = False
            self.assertEqual(browser.open('/root/infrae'), 302)
            self.assertTrue('Last-Modified' in browser.headers)
            self.assertTrue('Location' in browser.headers)
            self.assertEqual(
                browser.headers['Location'],
                'http://localhost/root/folder/test')

        # If you set the target to 0 the reference should be gone
        link.set_target(0)
        reference = getUtility(IReferenceService).get_reference(
            link, name=u"link")
        self.assertEqual(reference, None)

    def test_broken_relative_link(self):
        """Test rendering a broken relative link.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addLink('borken', 'Infrae', relative=True)

        IPublicationWorkflow(self.root.borken).publish()
        with self.layer.get_browser(public_settings) as browser:
            browser.options.follow_redirect = False
            browser.options.handle_errors = False
            self.assertEqual(
                browser.open('/root/borken'),
                200)
            self.assertEqual(
                browser.inspect.title,
                ['Infrae'])
            self.assertIn(
                'This link is currently broken.',
                browser.inspect.content[0])

    def test_closed(self):
        """Test viewing a closed link. You should get a message that
        it isn't viewable.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addLink(
            'infrae', 'Infrae', relative=True, target=self.root.test)

        IPublicationWorkflow(self.root.infrae).publish()
        IPublicationWorkflow(self.root.infrae).close()

        with self.layer.get_browser(public_settings) as browser:
            browser.options.follow_redirect = False
            self.assertEqual(
                browser.open('/root/infrae'),
                200)
            self.assertEqual(
                browser.inspect.content,
                ['Sorry, this Silva Link is not viewable.'])
            browser.login('editor')
            self.assertEqual(
                browser.open('/root/++preview++/infrae'),
                200)
            self.assertEqual(
                browser.inspect.title,
                ['Infrae'])
            self.assertIn(
                'This link redirects to http://localhost/root/++preview++/test.',
                browser.inspect.content[0])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkTestCase))
    return suite
