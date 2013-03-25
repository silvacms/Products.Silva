# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from datetime import datetime, timedelta
from DateTime import DateTime

from Products.Silva.testing import FunctionalLayer

from silva.core.interfaces import (IPublicationWorkflow,
                                   VersioningError, IVersion)
from zope.interface.verify import verifyObject


class PublicationWorkflowTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
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

        with self.assertRaises(VersioningError):
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
        self.assertTrue(content.is_published())

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
        self.assertEqual(
            content.get_unapproved_version_expiration_datetime(),
            None)
        self.assertEqual(
            content.get_unapproved_version_publication_datetime(),
            None)

    def test_new_version_pusblish_with_expiration_datetime_in_future(self):
        """If you make a new version of a published version that have
        an expiration date in the future it is kept.
        """
        content = self.root.test
        expiration_time = DateTime() + 30
        content.set_unapproved_version_expiration_datetime(expiration_time)

        publisher = IPublicationWorkflow(content)
        publisher.publish()
        self.assertTrue(content.is_published())

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
        self.assertEqual(
            content.get_unapproved_version_expiration_datetime(),
            expiration_time)
        self.assertEqual(
            content.get_unapproved_version_publication_datetime(),
            None)

    def test_new_version_closed_with_expiration_datetime_in_past(self):
        """If you make a new version out of a published version that
        have an expiration date in the past, it is not kept.
        """
        content = self.root.test
        expiration_time = DateTime() - 30
        content.set_unapproved_version_expiration_datetime(expiration_time)

        publisher = IPublicationWorkflow(content)
        publisher.publish()
        self.assertFalse(content.is_published())

        # The version is directly closed, because it is expired.
        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), '0')

        publisher.new_version()
        self.assertFalse(content.is_published())

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '1')
        self.assertEqual(content.get_last_closed_version(), '0')
        self.assertEqual(
            content.get_unapproved_version_expiration_datetime(),
            None)
        self.assertEqual(
            content.get_unapproved_version_publication_datetime(),
            None)

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

    def test_request_approval_published_version(self):
        """ request approval on already publish version must fail with
        exception.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        publisher.publish()
        with self.assertRaises(VersioningError):
            publisher.request_approval("please approve.")

        self.assertFalse(content.is_approval_requested())


    def test_request_approval(self):
        """ request approval on unapproved version (normal scenario)
        """
        content = self.root.test
        message = 'please approve.'
        publisher = IPublicationWorkflow(content)
        publisher.request_approval(message)

        self.assertTrue(content.is_approval_requested())

        with self.assertRaises(VersioningError):
            publisher.request_approval("please approve.")

    def test_withdraw(self):
        """ withdraw request for approval (normal scenario)
        """
        content = self.root.test
        message = 'please approve.'
        publisher = IPublicationWorkflow(content)
        publisher.request_approval(message)

        self.assertTrue(publisher.withdraw_request('made a mistake'))
        self.assertFalse(content.is_approval_requested())

        with self.assertRaises(VersioningError):
            publisher.withdraw_request('make an other mistake')

    def test_reject(self):
        """ reject request for approval (normal scenario)
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        publisher.request_approval('please approve')

        self.assertTrue(publisher.reject_request('u made a mistake'))
        self.assertFalse(content.is_approval_requested())

        with self.assertRaises(VersioningError):
            publisher.reject_request('u suck anyway')

    def test_reject_published(self):
        """ rejecting a published content must fail.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        publisher.request_approval('please approve')

        publisher.publish()

        self.assertFalse(content.is_approval_requested())

        with self.assertRaises(VersioningError):
            publisher.reject_request('u suck anyway')

    def test_revoke_approval(self):
        """ revoke approval, on approved content (normal scenario)
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        publisher.approve(datetime.now() + timedelta(1))

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), '0')
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

        self.assertTrue(publisher.revoke_approval())

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

    def test_revoke_approval_published(self):
        """ datetime for approval is in the past so the content get
        published and cannot be revoked.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        publisher.approve(datetime.now() - timedelta(1))

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

        with self.assertRaises(VersioningError):
            publisher.revoke_approval()

        self.assertEqual(content.get_public_version(), '0')
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), None)
        self.assertEqual(content.get_last_closed_version(), None)

    def test_revoke_approval_no_approved(self):
        """ revoke approval on non-approved content must fail.
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

        with self.assertRaises(VersioningError):
            publisher.revoke_approval()

        self.assertEqual(content.get_public_version(), None)
        self.assertEqual(content.get_approved_version(), None)
        self.assertEqual(content.get_unapproved_version(), '0')
        self.assertEqual(content.get_last_closed_version(), None)

    def test_get_versions(self):
        """ get versions ordered by id
        """
        content = self.root.test
        publisher = IPublicationWorkflow(content)
        for i in range(0, 10):
            publisher.publish()
            publisher.new_version()

        versions = publisher.get_versions()
        self.assertEquals(11, len(versions))
        for version in versions:
            self.assertTrue(IVersion.providedBy(version))
            self.assertTrue(content, version.get_content())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicationWorkflowTestCase))
    return suite
