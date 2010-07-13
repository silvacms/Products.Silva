# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from silva.core import interfaces
from zope.interface.verify import verifyObject

from Acquisition import aq_chain
from Products.Silva.testing import (
    FunctionalLayer, http, TestCase, get_event_names)
from Products.Silva.tests.helpers import publish_object


class LinkTestCase(TestCase):
    """Test Silva links.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def test_link(self):
        """Test that link triggers events.
        """
        # Clear previously created events.
        get_event_names()

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addLink('link', 'Link')

        # A link comes with the a version, so the list of triggered
        # events is pretty long.
        self.assertEquals(
            get_event_names(),
            ['ObjectWillBeAddedEvent', 'ObjectAddedEvent',
             'IntIdAddedEvent', 'ContainerModifiedEvent',
             'ObjectWillBeAddedEvent', 'ObjectAddedEvent',
             'IntIdAddedEvent', 'ObjectWillBeAddedEvent',
             'ObjectAddedEvent', 'IntIdAddedEvent',
             'ContainerModifiedEvent', 'ContainerModifiedEvent',
             'ObjectCreatedEvent', 'ObjectCreatedEvent'])

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

        response = http('GET /root/infrae HTTP/1.1', parsed=True)
        self.assertEqual(response.getStatus(), 302)
        headers = response.getHeaders()
        self.failUnless('Location' in headers.keys())
        self.assertEqual(headers['Location'], 'http://infrae.com')

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
            aq_chain(link.get_target()), aq_chain(self.root.document))
        self.assertEqual(link.get_relative(), True)

        response = http('GET /root/infrae HTTP/1.1', parsed=True)
        self.assertEqual(response.getStatus(), 302)
        headers = response.getHeaders()
        self.failUnless('Location' in headers.keys())
        self.assertEqual(
            headers['Location'],
            'http://localhost/root/document')

        # If we move the document around, the link will still work
        token = self.root.manage_cutObjects(['document'])
        self.root.folder.manage_pasteObjects(token)

        response = http('GET /root/infrae HTTP/1.1', parsed=True)
        self.assertEqual(response.getStatus(), 302)
        headers = response.getHeaders()
        self.failUnless('Location' in headers.keys())
        self.assertEqual(
            headers['Location'],
            'http://localhost/root/folder/document')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LinkTestCase, 'test'))
    return suite
