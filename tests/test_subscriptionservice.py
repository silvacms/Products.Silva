# Copyright (c) 2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase

from Products.Silva.adapters import subscribable
from Products.Silva import MAILHOST_ID, MAILDROPHOST_AVAILABLE

import mocksmtpserver

if MAILDROPHOST_AVAILABLE:
    from Testing import ZopeTestCase
    ZopeTestCase.installProduct('MaildropHost')

from Products.Silva import subscriptionerrors as errors    
    
class SubscriptionServiceTestCase(SilvaTestCase.SilvaTestCase):
    """Test the Subscription Service.
    """
    def afterSetUp(self):
        self.service = getattr(self.root, 'service_subscriptions')
        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        self.folder = self.add_folder(self.root, 'folder', u'Test Folder')
        self.ghost = self.add_ghost(self.root, 'ghost', 'contenturl')
        self.link = self.add_link(self.root, 'link', u'Test Link', 'url')
        # will be used by Mail(drop)Host
        self.smtpserver = mocksmtpserver.MockSMTPServer()
        mailhostservice = getattr(self.root, MAILHOST_ID)
        mailhostservice.smtp_host = 'localhost'
        mailhostservice.smtp_port = 8025
    
    def beforeTearDown(self):
        self.smtpserver.close()

    def test_requestSubscription(self):
        # XXX only test the exception-raising code paths, since I don't
        # yet know how to test the email sending
        path = self.doc.getPhysicalPath() + ('foobar', )
        emailaddress = "foo@localhost"
        self._testException(
            errors.SubscriptionError, 
            'path does not lead to a content object',
            self.service.requestSubscription, path, emailaddress)
        path = self.service.getPhysicalPath() # use something not subscribable
        emailaddress = "foo@localhost"
        self._testException(
            errors.SubscriptionError, 
            'content is not subscribable',
            self.service.requestSubscription, path, emailaddress)
        # even if all parameters are correct, content has to have its subscribability set
        path = self.doc.getPhysicalPath()
        emailaddress = "foo@localhost"
        self._testException(
            errors.SubscriptionError, 
            'content is not subscribable',
            self.service.requestSubscription, path, emailaddress)
        # Set subscribability, invalid emailaddress though
        path = self.doc.getPhysicalPath()
        emailaddress = "foo bar baz"
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        self._testException(
            errors.EmailaddressError, 
            'emailaddress not valid',
            self.service.requestSubscription, path, emailaddress)
        # emailaddress already subscribed
        path = self.doc.getPhysicalPath()
        emailaddress = "foo@localhost.com"
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscr.subscribe(emailaddress)
        self._testException(
            errors.EmailaddressError, 
            'emailaddress already subscribed',
            self.service.requestSubscription, path, emailaddress)

    def test_requestCancellation(self):
        # XXX only test the exception-raising code paths, since I don't
        # yet know how to test the email sending
        path = self.doc.getPhysicalPath() + ('foobar', )
        emailaddress = "foo@localhost"
        self._testException(
            errors.SubscriptionError, 
            'path does not lead to a content object',
            self.service.requestCancellation, path, emailaddress)
        path = self.service.getPhysicalPath() # use something not subscribable
        emailaddress = "foo@localhost"
        self._testException(
            errors.SubscriptionError, 
            'content does not support subscriptions',
            self.service.requestCancellation, path, emailaddress)
        # invalid emailaddress
        path = self.doc.getPhysicalPath()
        emailaddress = "foo bar baz"
        self._testException(
            errors.EmailaddressError, 
            'emailaddress not valid',
            self.service.requestCancellation, path, emailaddress)
        # emailaddress was not subscribed
        path = self.doc.getPhysicalPath()
        emailaddress = "foo@localhost.com"
        self._testException(
            errors.EmailaddressError, 
            'emailaddress was not subscribed',
            self.service.requestCancellation, path, emailaddress)
            
    def _testException(self, klass, message, method, *args, **kwargs):
        try:
            method(*args, **kwargs)
        except klass, e:
            self.assertEquals(message, str(e))
    
    def test__sendConfirmationRequest(self):
        path = self.doc.getPhysicalPath()
        emailaddress = "foo@localhost"
        subscr = subscribable.getSubscribable(self.doc)
        token = subscr.generateConfirmationToken(emailaddress)
        subscr = subscribable.getSubscribable(self.doc)
        # XXX how to continue to test the sending of the email??
        #self.service._sendConfirmationEmail(
        #    self.doc, emailaddress, token, 
        #    'subscription_confirmation_template', 'subscribe')
        #message = self.smtpserver.getMessagesDict()[self.service.sender]
        #self.assertEquals(emailaddress, message.recipients)

    def test_subscribe(self):
        ref = self.service._create_ref(self.doc)
        emailaddress = "foo1@bar.com"
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        token = subscr.generateConfirmationToken(emailaddress)
        self.service.subscribe(ref, emailaddress, token)
        self.assertEquals(True, subscr.isSubscribed(emailaddress))
        # and again, should raise an exception
        self.assertRaises(
            errors.SubscriptionError, 
            self.service.subscribe, ref, emailaddress, token)
        # for an invalid content ref an exception should be raised too
        ref = self.service._create_ref(self.service) # use something not subscribable
        emailaddress = "foo2@bar.com"
        token = subscr.generateConfirmationToken(emailaddress)
        self.assertRaises(
            errors.SubscriptionError, 
            self.service.subscribe, ref, emailaddress, token)

    def test_unsubscribe(self):
        ref = self.service._create_ref(self.doc)
        emailaddress = "foo1@bar.com"
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        token = subscr.generateConfirmationToken(emailaddress)
        self.service.subscribe(ref, emailaddress, token)
        token = subscr.generateConfirmationToken(emailaddress)
        self.service.unsubscribe(ref, emailaddress, token)
        # and again, should raise an exception
        self.assertRaises(
            errors.SubscriptionError, 
            self.service.unsubscribe, ref, emailaddress, token)
        # for an invalid content ref an exception should be raised too
        emailaddress = "foo2@bar.com"
        token = subscr.generateConfirmationToken(emailaddress)
        self.service.subscribe(ref, emailaddress, token)
        token = subscr.generateConfirmationToken(emailaddress)
        ref = self.service._create_ref(self.service) # use something not subscribable
        self.assertRaises(
            errors.SubscriptionError, 
            self.service.unsubscribe, ref, emailaddress, token)

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SubscriptionServiceTestCase))
    return suite

if __name__ == '__main__':
    framework()
