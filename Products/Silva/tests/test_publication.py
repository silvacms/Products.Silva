# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.tests.mockers import install_mockers
from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow, PublicationWorkflowError
from zope.interface.verify import verifyObject


class PublicationWorkflowTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        install_mockers(self.root)
        self.layer.login('editor')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('test', 'Test Content')

    def test_implementation(self):
        publisher = IPublicationWorkflow(self.root, None)
        self.assertEqual(publisher, None)

        publisher = IPublicationWorkflow(self.root.test, None)
        self.assertNotEqual(publisher, None)
        self.assertTrue(verifyObject(IPublicationWorkflow, publisher))

    def test_new_version_unapproved(self):
        """Create a new version while there is a unapproved one
        available. This is not possible.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

        with self.assertRaises(PublicationWorkflowError):
            publisher.new_version()

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

    def  test_new_version_published(self):
        """Create a new version while there is a published version.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        publisher.publish()

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

        publisher.new_version()
        self.assertTrue(content.is_published())

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '1')
        self.assertEqual(content.get_last_closed_version(), None)

    def test_publish_unapproved(self):
        """Publish an unapproved content.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

        publisher.publish()
        self.assertTrue(content.is_published())

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

    def test_close_published(self):
        """Close a published content
        """
        content = self.root.test
        # Need to publish content first.
        publisher = IPublicationWorkflow(content)
        publisher.publish()

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

        publisher = IPublicationWorkflow(content)
        publisher.close()
        self.assertFalse(content.is_published())

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), '0')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicationWorkflowTestCase))
    return suite
