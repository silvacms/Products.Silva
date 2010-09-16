# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import re
import urllib
from smtplib import SMTPException

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS import Folder
from OFS.CopySupport import _cb_encode, _cb_decode

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import MAILDROPHOST_AVAILABLE, MAILHOST_ID
from Products.Silva import subscriptionerrors as errors
from Products.Silva.adapters import subscribable
from Products.Silva.mail import sendmail
from Products.Silva.install import add_helper, fileobject_add_helper

from five import grok
from silva.core import conf as silvaconf
from silva.core.interfaces import IHaunted, IVersionedContent
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ISubscriptionService
from silva.translations import translate as _
from zope.component import queryUtility
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zeam.form import silva as silvaforms


class SubscriptionService(Folder.Folder, SilvaService):
    """Subscription Service
    """
    grok.implements(ISubscriptionService)
    default_service_identifier = 'service_subscriptions'

    meta_type = "Silva Subscription Service"
    silvaconf.icon('www/subscription_service.png')

    manage_options = (
        {'label':'Edit', 'action':'manage_subscriptions'}
        ,) + Folder.Folder.manage_options

    security = ClassSecurityInfo()

    # subscriptions are disabled by default
    _enabled = False

    # ZMI methods

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'enableSubscriptions')
    def enableSubscriptions(self):
        """Called TTW from ZMI to enable the feature
        """
        self._enabled = True

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'disableSubscriptions')
    def disableSubscriptions(self):
        """Called TTW from ZMI to disable the feature
        """
        self._enabled = False

    security.declareProtected(SilvaPermissions.View, 'subscriptionsEnabled')
    def subscriptionsEnabled(self):
        return self._enabled

    # Called from subscription UI

    security.declareProtected(SilvaPermissions.View, 'isSubscribable')
    def isSubscribable(self, content):
        # Convenience method to quickly determine if content is
        # subscribable, without having to get the content's
        # subscribable-adapter for it - e.g. in a pagetemplate.
        adapted = subscribable.getSubscribable(content)
        if adapted is None:
            return False
        return adapted.isSubscribable()

    security.declareProtected(SilvaPermissions.View, 'requestSubscription')
    def requestSubscription(self, content, emailaddress):
        # Send out request for subscription
        # NOTE: no doc string, so, not *publishable* TTW
        #
        adapted = subscribable.getSubscribable(content)
        # see if content is subscribable
        if adapted is None or not adapted.isSubscribable():
            raise errors.NotSubscribableError()
        # validate address
        if not self._isValidEmailaddress(emailaddress):
            raise errors.InvalidEmailaddressError()
        # generate confirmation token using adapter
        token = adapted.generateConfirmationToken(emailaddress)
        # check if not yet subscribed
        subscription = adapted.getSubscription(emailaddress)
        if subscription is not None:
            # send an email informing about this situation
            self._sendSuperfluousSubscriptionRequestEmail(
                content, emailaddress, token, 'already_subscribed_template',
                'confirm_subscription', subscription.contentSubscribedTo())
            raise errors.AlreadySubscribedError()
        # send confirmation email to emailaddress
        self._sendConfirmationEmail(
            content, emailaddress, token,
            'subscription_confirmation_template', 'confirm_subscription')

    security.declareProtected(SilvaPermissions.View, 'requestCancellation')
    def requestCancellation(self, content, emailaddress):
        # Send out request for cancellation of the subscription
        # NOTE: no doc string, so, not *publishable* TTW
        #
        adapted = subscribable.getSubscribable(content)
        # see if content is subscribable
        if adapted is None:
            raise errors.NotSubscribableError()
        # validate address
        if not self._isValidEmailaddress(emailaddress):
            raise errors.InvalidEmailaddressError()
        # check if indeed subscribed
        if not adapted.isSubscribed(emailaddress):
            # send an email informing about this situation
            self._sendSuperfluousCancellationRequestEmail(
                content, emailaddress, 'not_subscribed_template')
            raise errors.NotSubscribedError()
        # generate confirmation token using adapter
        token = adapted.generateConfirmationToken(emailaddress)
        # send confirmation email to emailaddress
        self._sendConfirmationEmail(
            content, emailaddress, token,
            'cancellation_confirmation_template', 'confirm_cancellation')

    # Called from subscription confirmation UI

    security.declareProtected(SilvaPermissions.View, 'subscribe')
    def subscribe(self, ref, emailaddress, token):
        # Check and confirm subscription
        # NOTE: no doc string, so, not *publishable* TTW
        #
        context = self._resolve_ref(ref)
        subscr = subscribable.getSubscribable(context)
        if subscr is None:
            raise errors.SubscriptionError()
        emailaddress = urllib.unquote(emailaddress)
        if not subscr.isValidSubscription(emailaddress, token):
            raise errors.SubscriptionError()
        subscr.subscribe(emailaddress)

    security.declareProtected(SilvaPermissions.View, 'unsubscribe')
    def unsubscribe(self, ref, emailaddress, token):
        # Check and confirm cancellation
        # NOTE: no doc string, so, not *publishable* TTW
        #
        context = self._resolve_ref(ref)
        subscr = subscribable.getSubscribable(context)
        if subscr is None:
            raise errors.CancellationError()
        emailaddress = urllib.unquote(emailaddress)
        if not subscr.isValidCancellation(emailaddress, token):
            raise errors.CancellationError()
        subscr.unsubscribe(emailaddress)

    # Helpers

    def _metadata(self, content, setname, fieldname):
        metadata_service = content.service_metadata
        version = content.get_viewable()
        value = metadata_service.getMetadataValue(version, setname, fieldname)
        if type(value) == type(u''):
            value = value.encode('utf-8')
        return value

    _emailpattern = re.compile(
        '^[0-9a-zA-Z_&.%+-]+@([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-zA-Z])?\.)+[a-zA-Z]{2,6}$')

    def _isValidEmailaddress(self, emailaddress):
        if self._emailpattern.search(emailaddress.lower()) == None:
            return False
        return True

    def _sendNotificationEmail(self, content):
        data = {}
        data['contenturl'] = content.absolute_url()
        data['contenttitle'] = content.get_title().encode('utf-8')
        data['subject'] = self._metadata(content, 'silva-extra', 'subject')
        data['description'] = self._metadata(content, 'silva-extra', 'content_description')
        adapted = subscribable.getSubscribable(content)
        assert adapted # content should support subscriptions
        template = str(self['publication_event_template'])
        subscriptions = adapted.getSubscriptions()
        for subscription in subscriptions:
            contentsubscribedto = subscription.contentSubscribedTo()
            data['subscribedcontenturl'] = contentsubscribedto.absolute_url()
            data['serviceurlforsubscribedcontent'] = \
                contentsubscribedto.absolute_url() + '/public/subscriptor'
            data['toaddress'] = subscription.emailaddress()
            self._sendEmail(template, data)

    def _sendSuperfluousCancellationRequestEmail(
        self, content, emailaddress, template_id):
        template = str(self[template_id])
        data = {}
        data['toaddress'] = emailaddress
        data['contenturl'] = content.absolute_url()
        data['contenttitle'] = content.get_title().encode('utf-8')
        self._sendEmail(template, data)

    def _sendSuperfluousSubscriptionRequestEmail(
        self, content, emailaddress, token, template_id, action, subscribedcontent):
        ref = self._create_ref(content)
        template = str(self[template_id])
        data = {}
        data['toaddress'] = emailaddress
        data['contenturl'] = content.absolute_url()
        data['contenttitle'] = content.get_title().encode('utf-8')
        emailaddress = urllib.quote(emailaddress)
        data['confirmationurl'] = '%s/public/%s?ref=%s&emailaddress=%s&token=%s' % (
            content.absolute_url(), action, ref, emailaddress, token)
        data['subscribedcontenturl'] = subscribedcontent.absolute_url()
        data['serviceurlforsubscribedcontent'] = \
            subscribedcontent.absolute_url() + '/public/subscriptor'
        self._sendEmail(template, data)

    def _sendConfirmationEmail(
        self, content, emailaddress, token, template_id, action):
        ref = self._create_ref(content)
        template = str(self[template_id])
        data = {}
        data['toaddress'] = emailaddress
        data['contenturl'] = content.absolute_url()
        data['contenttitle'] = content.get_title().encode('utf-8')
        emailaddress = urllib.quote(emailaddress)
        data['confirmationurl'] = '%s/public/%s?ref=%s&emailaddress=%s&token=%s' % (
            content.absolute_url(), action, ref, emailaddress, token)
        self._sendEmail(template, data)

    def _sendEmail(self, template, data):
        message = template % data
        try:
            sendmail(self, message)
        except SMTPException:
            import sys, zLOG
            zLOG.LOG('Silva service_subscriptions', zLOG.PROBLEM,
                     'sending mail failed', sys.exc_info())

    def _create_ref(self, content):
        """Create encoded reference to object.
        """
        return _cb_encode(content.getPhysicalPath())

    def _resolve_ref(self, ref):
        """Decode and resolve reference to object.
        """
        return self.unrestrictedTraverse(_cb_decode(ref))

    security.declareProtected(
        SilvaPermissions.ViewAuthenticated, 'security_trigger')
    def security_trigger(self):
        pass

InitializeClass(SubscriptionService)


class SubscriptionServiceManagementView(silvaforms.ZMIComposedForm):
    """Edit File Serivce.
    """
    grok.require('zope2.ViewManagementScreens')
    grok.name('manage_subscriptions')
    grok.context(SubscriptionService)

    label = _(u"Configure subscriptions")


class SubscriptionServiceActivateForm(silvaforms.ZMISubForm):
    grok.context(SubscriptionService)
    silvaforms.view(SubscriptionServiceManagementView)
    silvaforms.order(20)

    label = _(u"Activate subscriptions")
    description = _(u"Activate sending emails notifications")

    def available(self):
        return not self.context.subscriptionsEnabled()

    @silvaforms.action(_(u'Activate'))
    def action_activate(self):
        self.context.enableSubscriptions()
        self.status = _(u"Subscriptions activated.")
        return silvaforms.SUCCESS


class SubscriptionServiceDisableForm(silvaforms.ZMISubForm):
    grok.context(SubscriptionService)
    silvaforms.view(SubscriptionServiceManagementView)
    silvaforms.order(25)

    label = _(u"Disable subscriptions")
    description = _(u"Disable sending emails notifications")

    def available(self):
        return self.context.subscriptionsEnabled()

    @silvaforms.action(_(u'Disable'))
    def action_disable(self):
        self.context.disableSubscriptions()
        self.status = _(u"Subscriptions disabled.")
        return silvaforms.SUCCESS


class SubscriptionServiceInstallMaildropHostForm(silvaforms.ZMISubForm):
    grok.context(SubscriptionService)
    silvaforms.view(SubscriptionServiceManagementView)
    silvaforms.order(30)

    label = _(u"Install MaildropHost")
    description = _(u"Install a MaildropHost service to send emails")

    def available(self):
        if not MAILDROPHOST_AVAILABLE:
            return False
        root = self.context.get_root()
        mailhost =  getattr(root, MAILHOST_ID, None)
        return mailhost is None or mailhost.meta_type != 'Maildrop Host'

    @silvaforms.action(_(u'Install'))
    def action_install(self):
        root = self.context.get_root()
        if hasattr(root, MAILHOST_ID):
            root.manage_delObjects([MAILHOST_ID, ])
        factory = root.manage_addProduct['MaildropHost']
        factory.manage_addMaildropHost(
            MAILHOST_ID, 'Spool based mail delivery')
        self.status = (
            u'New mailhost object installed. '
            u'The system adminstator should take care of '
            u'starting the mail delivery process.')


@grok.subscribe(ISubscriptionService, IObjectCreatedEvent)
def service_created(service, event):
    """Add all default templates to the service.
    """
    for identifier in [
        'subscription_confirmation_template',
        'already_subscribed_template',
        'cancellation_confirmation_template',
        'not_subscribed_template',
        'publication_event_template']:
        add_helper(
            service, identifier, globals(), fileobject_add_helper, True)


@grok.subscribe(IVersionedContent, IContentPublishedEvent)
def content_published(content, event):
    """Content have been published. Send notifications.
    """
    service = queryUtility(ISubscriptionService)
    if service is not None:
        # first send notification for content
        service._sendNotificationEmail(content)
        # now send email for potential haunting ghosts
        for haunting in IHaunted(content).getHauting():
            service._sendNotificationEmail(haunting)
