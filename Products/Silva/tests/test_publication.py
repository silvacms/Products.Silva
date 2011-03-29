# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import IPublicationWorkflow
from zope.interface.verify import verifyObject


class MockupVersion(Version):
    meta_type='MockupVersion'


class MockupVersionedContent(VersionedContent):
    meta_type='MockupVersionedContent'

    def __init__(self, *args):
        super(MockupVersionedContent, self).__init__(*args)
        self.create_mockup_version('0')

    def create_mockup_version(self, version_id):
        self._setObject(str(version_id), MockupVersion(str(version_id)))
        self.create_version(str(version_id), None, None)


class PublicationWorkflowTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.root._setObject('content', MockupVersionedContent('content'))

    def test_implementation(self):
        publisher = IPublicationWorkflow(self.root, None)
        self.assertEqual(publisher, None)

        publisher = IPublicationWorkflow(self.root.content, None)
        self.assertNotEqual(publisher, None)
        self.assertTrue(verifyObject(IPublicationWorkflow, publisher))

    def test_publish_unapproved(self):
        """Publish an unapproved content.
        """
        content = self.root.content
        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

        publisher = IPublicationWorkflow(content)
        publisher.publish()

        self.assertTrue(content.is_published())

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

    def test_close_published(self):
        """Close a published content
        """
        content = self.root.content
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
