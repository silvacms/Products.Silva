# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import re
import urllib
import logging

# Zope
from OFS import Folder
from OFS.CopySupport import _cb_encode, _cb_decode
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Silva
from Products.Silva import helpers
from Products.Silva import SilvaPermissions
from Products.Silva import MAILDROPHOST_AVAILABLE, MAILHOST_ID
from Products.Silva import subscriptionerrors as errors
from Products.Silva.adapters import subscribable
from Products.SilvaLayout.interfaces import IMetadata
from Products.Silva.mail import sendmail

from five import grok
from silva.core import conf as silvaconf
from silva.core.interfaces import IHaunted, ISubscribable
from silva.core.interfaces.service import ISilvaLocalService
from silva.core.services.base import SilvaService
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent

logger = logging.getLogger('silva.app.subscriptions')


class SubscriptionService(Folder.Folder, SilvaService):
    """Subscription Service
    """
    grok.implements(ISilvaLocalService)

    meta_type = "Silva Subscription Service"
    silvaconf.icon('www/subscription_service.png')

    manage_options = (
        ({'label':'Edit', 'action':'manage_editSubscriptionServiceForm'}, ) +
        Folder.Folder.manage_options
        )

    silvaconf.factory('manage_addSubscriptionServiceForm')
    silvaconf.factory('manage_addSubscriptionService')

    security = ClassSecurityInfo()

    # subscriptions are disabled by default
    _enabled = False
    _from = 'Subscription Service <subscription-service@example.com>'

    # ZMI methods

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editSubscriptionServiceForm')
    manage_editSubscriptionServiceForm = PageTemplateFile(
        "www/subscriptionServiceEdit.pt", globals(),
        __name__='manage_editSubscriptionServiceForm')

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'isMaildropHostAvailable')
    def isMaildropHostAvailable(self):
        return MAILDROPHOST_AVAILABLE

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'isMaildropHostInstalled')
    def isMaildropHostInstalled(self):
        silvaroot = self.get_root()
        mailhost =  getattr(silvaroot, MAILHOST_ID, None)
        return mailhost is not None and mailhost.meta_type == 'Maildrop Host'

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'installMaildropHost')
    def installMaildropHost(self):
        """Called TTW from ZMI to install a maildrophost object
        """
        silvaroot = self.get_root()
        if hasattr(silvaroot, MAILHOST_ID):
            silvaroot.manage_delObjects([MAILHOST_ID, ])
        from Products import MaildropHost
        MaildropHost.manage_addMaildropHost(
            silvaroot, MAILHOST_ID, 'Spool based mail delivery')
        return self.manage_editSubscriptionServiceForm(
            manage_tabs_message=(
                'New mailhost object installed. '
                'The system adminstator should take care of '
                'starting the mail delivery process'))

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'enableSubscriptions')
    def enableSubscriptions(self):
        """Called TTW from ZMI to enable the feature
        """
        self._enabled = True
        return self.manage_editSubscriptionServiceForm(
            manage_tabs_message=('Subscriptions enabled'))

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'disableSubscriptions')
    def disableSubscriptions(self):
        """Called TTW from ZMI to disable the feature
        """
        self._enabled = False
        return self.manage_editSubscriptionServiceForm(
            manage_tabs_message=('Subscriptions disabled'))

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
            self._send_confirmation(
                content, subscription.contentSubscribedTo(), emailaddress, token,
                'already_subscribed_template', 'confirm_subscription')
            raise errors.AlreadySubscribedError()

        # send confirmation email to emailaddress
        self._send_confirmation(
            content, content, emailaddress, token,
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
            self._send_information(
                content, emailaddress, 'not_subscribed_template')
            raise errors.NotSubscribedError()
        # generate confirmation token using adapter
        subscription = adapted.getSubscription(emailaddress)
        content_subscribed = subscription.contentSubscribedTo()
        token = ISubscribable(content_subscribed).generateConfirmationToken(
            emailaddress)
        # send confirmation email to emailaddress
        self._send_confirmation(
            content, content_subscribed, emailaddress, token,
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

    # Notification trigger

    security.declareProtected(
        SilvaPermissions.ApproveSilvaContent, 'sendPublishNotification')
    def sendPublishNotification(self, content):
        if not self._enabled:
            return
        if not content.get_viewable():
            #content isn't published.  How could this method be called then?
            # on the status tab, if you set the expiration to an earlier date
            # than the publication date.
            return
        # first send notification for content
        self.send_notification(content, 'publication_event_template')
        # now send email for potential haunting ghosts
        adapted = IHaunted(content)
        thehaunting = adapted.getHaunting()
        for haunting in thehaunting:
            self.send_notification(haunting, 'publication_event_template')

    security.declarePrivate('send_notification')
    def send_notification(
        self, content, template_id='publication_event_template'):
        if not self.subscriptionsEnabled():
            return
        template = self._get_template(content, template_id)
        data = self._get_default_data(content)
        manager = ISubscribable(content)
        for subscription in manager.getSubscriptions():
            content_url = subscription.contentSubscribedTo().absolute_url()
            data['subscribed_content'] = subscription.contentSubscribedTo()
            data['service_url'] = content_url + '/public/subscriptor'
            data['to'] = subscription.emailaddress()
            self._send_email(template, data)

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

    def _get_template(self, content, template_id):
        if not template_id in self.objectIds():
            logger.error("Missing template %s for notification on %s." % (
                    template_id, repr(content)))
            raise KeyError(template_id)
        return aq_base(self[template_id]).__of__(content)

    def _get_default_data(self, content, email=None):
        data = {}
        data['from'] = self._from
        data['to'] = email
        data['metadata'] = IMetadata(content)
        data['sitename'] = self.get_root().get_title_or_id()
        data['confirmation_delay'] = '3'
        return data

    def _send_information(self, content, email, template_id):
        template = self._get_template(content, template_id)
        data = self._get_default_data(content, email)
        self._send_email(template, data)

    def _send_confirmation(
        self, content, subscribed_content, email, token, template_id, action):
        template = self._get_template(content, template_id)
        data = self._get_default_data(content, email)
        subscribed_content_url = subscribed_content.absolute_url()
        subscribed_content_id = self._create_ref(subscribed_content)
        data['confirmation_url'] = '%s/public/%s?%s' % (
            subscribed_content_url, action, urllib.urlencode((
                    ('ref', subscribed_content_id),
                    ('emailaddress', urllib.quote(email)),
                    ('token', token)),))
        data['subscribed_content'] = subscribed_content
        data['service_url'] = subscribed_content_url + '/public/subscriptor'
        self._send_email(template, data)

    def _send_email(self, template, data):
        message = template(**data)
        sendmail(self, message, mto=data['to'], mfrom=data['from'])

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

manage_addSubscriptionServiceForm = PageTemplateFile(
    "www/subscriptionServiceAdd.pt", globals(),
    __name__='manage_addSubscriptionServiceForm')

def manage_addSubscriptionService(context,
       id='service_subscriptions', title='', REQUEST=None):
    """Add subscription service.
    """
    service = SubscriptionService(id)
    service.title = 'Subscription Service'
    context._setObject(id, service)
    service = getattr(context, id)
    notify(ObjectCreatedEvent(service))
    helpers.add_and_edit(context, id, REQUEST)
    return ''

@grok.subscribe(SubscriptionService, IObjectCreatedEvent)
def service_created(service, event):
    """Add all default templates to the service.
    """
    from Products.Silva.install import add_helper, pt_add_helper
    for identifier in [
        'subscription_confirmation_template.pt',
        'already_subscribed_template.pt',
        'cancellation_confirmation_template.pt',
        'not_subscribed_template.pt',
        'publication_event_template.pt']:
        add_helper(service, identifier, globals(), pt_add_helper, True)
