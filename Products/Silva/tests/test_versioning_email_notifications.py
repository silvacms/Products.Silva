# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
import unittest
from datetime import datetime, timedelta


from zope.component import getUtility
from Products.Silva.testing import FunctionalLayer
from silva.core import interfaces
from silva.core.services import interfaces as service_interfaces


class EmailNotificationVersioningTestCase(unittest.TestCase):
    layer = FunctionalLayer

    users_with_email = ['reader', 'author', 'editor', 'chiefeditor', 'manager']

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

        get_member = getUtility(service_interfaces.IMemberService).get_member
        for user in self.users_with_email:
            get_member(user).set_email("%s@example.com" % user)
        message_service = getUtility(interfaces.IMessageService)
        message_service._enabled = True
        message_service._fromaddr = 'silva@example.com'

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['Silva']

        auth_manager = interfaces.IAuthorizationManager(self.root.folder)
        authorization = auth_manager.get_authorization(
            'reader', self.root.folder)
        authorization.grant('ChiefEditor')
        self.layer.logout()

        self.layer.login('author')
        factory.manage_addMockupVersionedContent('versioning', 'Versioning')
        self.layer.logout()
        self.versioning = self.root.folder.versioning
        self.publisher = interfaces.IPublicationWorkflow(self.versioning)

    def send_messages(self):
        getUtility(interfaces.IMessageService).send_pending_messages()

    def test_email_request_for_approval(self):
        self.layer.login('author')
        self.publisher.request_approval("Please approve")
        self.send_messages()
        self.assertEquals(1, len(self.root.service_mailhost.messages))
        email = self.root.service_mailhost.read_last_message()
        self.assertTrue(email)
        self.assertEquals('reader@example.com', email.headers['To'])
        self.assertEquals('author@example.com', email.headers['Reply-To'])
        self.assertEquals('Approval requested', email.headers['Subject'])
        self.assertTrue("Please approve" in email.message)

    def test_email_request_refused(self):
        self.layer.login('author')
        self.publisher.request_approval("Please approve")
        self.send_messages()
        self.layer.logout()

        self.layer.login('reader')
        self.publisher.reject_request("That's bad")
        self.send_messages()
        self.layer.logout()

        self.assertEquals(2, len(self.root.service_mailhost.messages))
        email = self.root.service_mailhost.messages[-1]
        self.assertEquals('author@example.com', email.headers['To'])
        self.assertEquals('reader@example.com', email.headers['Reply-To'])
        self.assertEquals('Approval rejected by editor', email.headers['Subject'])
        self.assertTrue("That's bad" in email.message)

    def test_email_request_withdraw(self):
        self.layer.login('author')
        self.publisher.request_approval("Please approve")
        self.send_messages()

        self.publisher.withdraw_request("I made a mistake")
        self.send_messages()
        self.layer.logout()

        self.assertEquals(2, len(self.root.service_mailhost.messages))
        email = self.root.service_mailhost.messages[-1]
        self.assertEquals('reader@example.com', email.headers['To'])
        self.assertEquals('author@example.com', email.headers['Reply-To'])
        self.assertEquals('Approval withdrawn by author',
            email.headers['Subject'])
        self.assertTrue("I made a mistake" in email.message)

    def test_email_request_approved(self):
        self.layer.login('author')
        self.publisher.request_approval("Please approve")
        self.send_messages()
        self.layer.logout()

        self.layer.login('reader')
        self.publisher.approve()
        self.send_messages()
        self.layer.logout()

        self.assertEquals(2, len(self.root.service_mailhost.messages))
        email = self.root.service_mailhost.messages[-1]
        self.assertEquals('author@example.com', email.headers['To'])
        self.assertEquals('reader@example.com', email.headers['Reply-To'])
        self.assertEquals('Version approved', email.headers['Subject'])

    def test_email_unapproved(self):
        self.layer.login('author')
        self.publisher.request_approval("Please approve")
        self.send_messages()
        self.layer.logout()

        self.layer.login('reader')
        self.publisher.approve(datetime.now() + timedelta(days=+1))
        self.send_messages()

        self.publisher.revoke_approval()
        self.send_messages()
        self.layer.logout()

        self.assertEquals(3, len(self.root.service_mailhost.messages))
        email = self.root.service_mailhost.messages[-1]
        self.assertEquals('author@example.com', email.headers['To'])
        self.assertEquals('reader@example.com', email.headers['Reply-To'])
        self.assertEquals('Unapproved', email.headers['Subject'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EmailNotificationVersioningTestCase))
    return suite
