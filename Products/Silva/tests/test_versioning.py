# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer
from Products.Silva.testing import assertTriggersEvents, assertNotTriggersEvents

from DateTime import DateTime
from Products.Silva import Versioning
from Products.Silva.Content import Content
from OFS.SimpleItem import SimpleItem


class MockupVersion(SimpleItem):
    meta_type='MockupVersion'

    def __init__(self, id):
        self.id = id


class MockupVersionedContent(Versioning.Versioning, Content, SimpleItem):
    meta_type='MockupVersionedContent'

    def __init__(self, id):
        self.id = id
        for version in range(0, 5):
            setattr(self, str(version), MockupVersion(str(version)))
            getattr(self, str(version)).title = 'Version %d' % version


class VersioningTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        self.root._setObject('versioning', MockupVersionedContent('versioning'))
        self.versioning = self.root.versioning

    def test_approve_publish(self):
        versioning = self.versioning
        # no version available
        self.assertEqual(versioning.get_public_version(),None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)

        # no version to approve
        self.assertRaises(
            Versioning.VersioningError,
            versioning.approve_version)

        # create new version
        versioning.create_version('0', DateTime() - 10, DateTime() + 10)
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')
        self.assertEqual(versioning.is_version_published(), False)

        # approve it
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), '0')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.is_version_published(), True)

        # already approved
        self.assertRaises(
            Versioning.VersioningError,
            versioning.approve_version)

        # create new version
        versioning.create_version('1', DateTime() - 10, DateTime() + 10)
        self.assertEqual(versioning.get_public_version(), '0')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '1')
        self.assertEqual(versioning.get_last_closed_version(), None)

        # approve last version. It will close the previous version to
        # publish the new one
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentClosedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), '1')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.get_last_closed_version(), '0')

    def test_approve_unapprove(self):
        versioning = self.versioning

        # no version yet
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)

        # create new version
        versioning.create_version('0', DateTime() + 10, DateTime() + 20)
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')
        self.assertEqual(versioning.is_version_approved(), False)

        # no version to unapprove
        self.assertRaises(
            Versioning.VersioningError,
            versioning.unapprove_version)

        # approve it but publication time is in the future
        with assertTriggersEvents('ContentApprovedEvent'):
            versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), '0')
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.is_version_approved(), True)

        # unapprove it
        with assertTriggersEvents('ContentUnApprovedEvent'):
            versioning.unapprove_version()
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')
        self.assertEqual(versioning.is_version_approved(), False)

        # change the time to something in the past, so it'll be published
        versioning.set_unapproved_version_publication_datetime(DateTime() - 10)

        # approve it
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), '0')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        # (version is published)
        self.assertEqual(versioning.is_version_approved(), False)

    def test_create_new_version_published(self):
        versioning = self.versioning

        # create new version
        versioning.create_version('0', DateTime() - 10, DateTime() + 20)

        # approve it
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()

        # it should be public now, create new version
        versioning.create_version('1', DateTime() - 5, DateTime() + 20)
        self.assertEqual(versioning.get_public_version(), '0')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '1')

    def test_close_publish(self):
        versioning = self.root.versioning

        # nothing to close
        self.assertRaises(
            Versioning.VersioningError,
            versioning.close_version)

        # create new version
        versioning.create_version('0', DateTime() + 10, DateTime() + 20)

        # change datetime
        versioning.set_unapproved_version_publication_datetime(DateTime() - 10)

        # unapproved versions cannot be closed
        self.assertRaises(
            Versioning.VersioningError,
            versioning.close_version)

        # now approve it
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), '0')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.get_last_closed_version(), None)

        with assertTriggersEvents('ContentClosedEvent'):
            versioning.close_version()

        # create new version
        versioning.create_version('1', DateTime() - 5, DateTime() + 20)
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '1')
        self.assertEqual(versioning.get_last_closed_version(), '0')

        # approve it
        with assertNotTriggersEvents(
            'ContentClosedEvent'):
            with assertTriggersEvents(
                'ContentApprovedEvent',
                'ContentPublishedEvent'):
                versioning.approve_version()
        # second should be public now, first is close
        self.assertEqual(versioning.get_public_version(), '1')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.get_last_closed_version(), '0')

    def test_close_two_versions(self):
        # test manual close
        versioning = self.versioning

        # create new version, publish it
        versioning.create_version('0', DateTime() - 10, DateTime() + 20)
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()

        # close it
        with assertTriggersEvents(
            'ContentClosedEvent'):
            versioning.close_version()

        self.assertEqual(versioning.get_previous_versions(), ['0'])
        self.assertEqual(versioning.get_last_closed_version(), '0')

        # create a new version
        versioning.create_version('1', DateTime() - 1, DateTime() + 2)
        with assertTriggersEvents(
            'ContentApprovedEvent',
            'ContentPublishedEvent'):
            versioning.approve_version()

        # close it
        with assertTriggersEvents(
            'ContentClosedEvent'):
            versioning.close_version()
        self.assertEqual(versioning.get_previous_versions(), ['0', '1'])
        self.assertEqual(versioning.get_last_closed_version(), '1')

    def test_consistency(self):
        versioning = self.versioning

        def _check_state(approved=0, approval_request=0, published=0):
            # helper method to check consistency of the version state
            self.assertEqual(
                approved, versioning.is_version_approved())
            self.assertEqual(
                approved and versioning.get_next_version() or None,
                self.versioning.get_approved_version())
            self.assertEqual(
                published, versioning.is_version_published())
            self.assertEqual(
                approval_request and not approved,
                versioning.is_version_approval_requested())
            self.assertEqual(
                (not approved) and versioning.get_next_version() or None,
                versioning.get_unapproved_version())

        # test request for approval
        _check_state()
        versioning.create_version('0', DateTime() + 10, None)
        _check_state()
        versioning.request_version_approval('message')
        _check_state(approval_request=1)
        versioning.withdraw_version_approval('Withdraw message')
        _check_state()
        versioning.request_version_approval('Request message')
        _check_state(approval_request=1)
        versioning.approve_version()
        _check_state(approved=1)

        # just check, if request for approval could break unaproval
        # or close later, though this is unreasonable
        versioning.unapprove_version()
        _check_state()
        versioning.approve_version()
        _check_state(approved=1)
        versioning.set_approved_version_publication_datetime(DateTime() - 10)
        versioning.close_version()
        _check_state()
        versioning.create_version('1', DateTime() + 10, None)
        _check_state()

    def test_request_approval_approved(self):
        versioning = self.versioning

        # Cannot ask approval if there is no version to approve
        self.assertRaises(
            Versioning.VersioningError,
            versioning.request_version_approval, 'Request message')

        self.assertEqual(versioning.is_version_approval_requested(), False)

        versioning.create_version('0', DateTime() + 10, None)
        with assertTriggersEvents('ContentRequestApprovalEvent'):
            versioning.request_version_approval('Request test message')

        self.assertEqual(versioning.is_version_approval_requested(), True)
        self.assertEqual(versioning.get_approval_requester(), 'manager')
        self.assertEqual(
            versioning.get_approval_request_message(),
            'Request test message')

        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')

        # Cannot ask approval two times
        self.assertRaises(
            Versioning.VersioningError,
            versioning.request_version_approval, 'Request message')

        with assertTriggersEvents('ContentApprovedEvent'):
            versioning.approve_version()

        self.assertEqual(versioning.is_version_approval_requested(), False)
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), '0')
        self.assertEqual(versioning.get_unapproved_version(), None)

        # It is approved, cannot ask to approve it again
        self.assertRaises(
            Versioning.VersioningError,
            versioning.request_version_approval, 'Request message')

    def test_request_approval_withdraw(self):
        versioning = self.versioning

        # Cannot ask/cancel approval if there is no version to approve
        self.assertRaises(
            Versioning.VersioningError,
            versioning.withdraw_version_approval, 'Withdraw message')

        versioning.create_version('0', DateTime() + 10, None)
        with assertTriggersEvents('ContentRequestApprovalEvent'):
            versioning.request_version_approval('Request message')

        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')

        with assertTriggersEvents('ContentApprovalRequestCanceledEvent'):
            versioning.withdraw_version_approval('Withdraw message')

        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')

        # Cannot withdraw version twice
        self.assertRaises(
            Versioning.VersioningError,
            versioning.withdraw_version_approval, 'Withdraw message')

    def test_request_approval_reject(self):
        versioning = self.versioning

        # Cannot reject approval if there is no version to approve
        self.assertRaises(
            Versioning.VersioningError,
            versioning.reject_version_approval, 'Reject message')

        versioning.create_version('0', DateTime() + 10, None)
        with assertTriggersEvents('ContentRequestApprovalEvent'):
            versioning.request_version_approval('Request message')

        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')

        with assertTriggersEvents('ContentApprovalRequestRefusedEvent'):
            versioning.reject_version_approval('Reject message')

        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), '0')

        # Cannot reject version twice
        self.assertRaises(
            Versioning.VersioningError,
            versioning.reject_version_approval, 'Reject message')

    def test_request_approval_invalid(self):
        versioning = self.versioning

        versioning.create_version('0', DateTime() + 10, None)
        versioning.approve_version()
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), '0')
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.get_last_closed_version(), None)

        # Cannot work on already approved version
        self.assertRaises(
            Versioning.VersioningError,
            versioning.request_version_approval, 'Request message')
        self.assertRaises(
            Versioning.VersioningError,
            versioning.withdraw_version_approval, 'Withdraw message')
        self.assertRaises(
            Versioning.VersioningError,
            versioning.reject_version_approval, 'Reject message')
        self.assertEqual(versioning.is_version_approval_requested(), False)

        self.versioning.set_approved_version_publication_datetime(
            DateTime() - 10)
        self.assertEqual(versioning.get_public_version(), '0')
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.get_last_closed_version(), None)

        # Cannot work on published version
        self.assertRaises(
            Versioning.VersioningError,
            versioning.request_version_approval, 'Request message')
        self.assertRaises(
            Versioning.VersioningError,
            versioning.withdraw_version_approval, 'Withdraw message')
        self.assertRaises(
            Versioning.VersioningError,
            versioning.reject_version_approval, 'Reject message')
        self.assertEqual(versioning.is_version_approval_requested(), False)

        versioning.close_version()
        self.assertEqual(versioning.get_public_version(), None)
        self.assertEqual(versioning.get_approved_version(), None)
        self.assertEqual(versioning.get_unapproved_version(), None)
        self.assertEqual(versioning.get_last_closed_version(), '0')

        # Cannot work on closed version
        self.assertRaises(
            Versioning.VersioningError,
            versioning.request_version_approval, 'Request message')
        self.assertRaises(
            Versioning.VersioningError,
            versioning.withdraw_version_approval, 'Withdraw message')
        self.assertRaises(
            Versioning.VersioningError,
            versioning.reject_version_approval, 'Reject message')
        self.assertEqual(versioning.is_version_approval_requested(), False)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(VersioningTestCase))
    return suite
