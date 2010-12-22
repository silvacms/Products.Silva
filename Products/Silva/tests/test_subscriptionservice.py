# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.adapters import subscribable
from Products.Silva import MAILHOST_ID
from Products.Silva import subscriptionerrors as errors    

import SilvaTestCase

def _patched_send(*args, **kwargs):
    return
   
class SubscriptionServiceTestCase(SilvaTestCase.SilvaTestCase):
    """Test the Subscription Service.
    """
    def afterSetUp(self):
        self.service = getattr(self.root, 'service_subscriptions')
        self.doc = self.add_document(self.root, 'doc', u'Test Document')
        self.folder = self.add_folder(self.root, 'folder', u'Test Folder')
        self.ghost = self.add_ghost(self.root, 'ghost', 'contenturl')
        self.link = self.add_link(self.root, 'link', u'Test Link', 'url')
        mailhost = self.root[MAILHOST_ID]
        self._old_send = mailhost._send
        mailhost._send = _patched_send
    
    def beforeTearDown(self):
        mailhost = self.root[MAILHOST_ID]
        mailhost._send = self._old_send

    def test_requestSubscription(self):
        # XXX only test the exception-raising code paths, since I don't
        # yet know how to test the email sending
        #
        # first use something not subscribable at all
        emailaddress = "foo@localhost"
        self.assertRaises(
            errors.NotSubscribableError, 
            self.service.requestSubscription, self.service, emailaddress)
        # even if all parameters are correct, content has to have its subscribability set
        emailaddress = "foo@localhost"
        self.assertRaises(
            errors.NotSubscribableError, 
            self.service.requestSubscription, self.doc, emailaddress)
        # Set subscribability, invalid emailaddress though
        emailaddress = "foo bar baz"
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        self.assertRaises(
            errors.InvalidEmailaddressError, 
            self.service.requestSubscription, self.doc, emailaddress)
        # emailaddress already subscribed
        emailaddress = "foo@localhost.com"
        subscr = subscribable.getSubscribable(self.doc)
        subscr.setSubscribability(subscribable.SUBSCRIBABLE)
        subscr.subscribe(emailaddress)
        self.service.requestSubscription(self.doc, emailaddress)

    def test_requestCancellation(self):
        # XXX only test the exception-raising code paths, since I don't
        # yet know how to test the email sending
        #
        # first use something not subscribable at all
        emailaddress = "foo@localhost"
        self.assertRaises(
            errors.NotSubscribableError,
            self.service.requestCancellation, self.service, emailaddress)
        # invalid emailaddress
        emailaddress = "foo bar baz"
        self.assertRaises(
            errors.InvalidEmailaddressError, 
            self.service.requestCancellation, self.doc, emailaddress)
        # emailaddress was not subscribed
        emailaddress = "foo@localhost.com"
        self.assertRaises(
            errors.NotSubscribedError, 
            self.service.requestCancellation, self.doc, emailaddress)
            
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
            errors.CancellationError, 
            self.service.unsubscribe, ref, emailaddress, token)
        # for an invalid content ref an exception should be raised too
        emailaddress = "foo2@bar.com"
        token = subscr.generateConfirmationToken(emailaddress)
        self.service.subscribe(ref, emailaddress, token)
        token = subscr.generateConfirmationToken(emailaddress)
        ref = self.service._create_ref(self.service) # use something not subscribable
        self.assertRaises(
            errors.CancellationError, 
            self.service.unsubscribe, ref, emailaddress, token)

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SubscriptionServiceTestCase))
    return suite
