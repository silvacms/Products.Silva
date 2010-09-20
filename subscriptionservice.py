# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import re
import urllib

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS import Folder
from zExceptions import NotFound

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import MAILDROPHOST_AVAILABLE, MAILHOST_ID
from Products.Silva import subscriptionerrors as errors
from Products.Silva.adapters import subscribable
from Products.Silva.mail import sendmail
from Products.Silva.install import add_helper, fileobject_add_helper

from five import grok
from silva.captcha import Captcha
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import ISilvaObject, IHaunted, IVersionedContent
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import ISubscriptionService
from silva.core.references.reference import get_content_id, get_content_from_id
from silva.translations import translate as _
from z3c.schema.email import RFC822MailAddress, isValidMailAddress
from zeam.form import silva as silvaforms
from zope import interface
from zope.component import queryUtility, getUtility
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from megrok.chameleon.components import ChameleonPageTemplate


class SubscriptionService(Folder.Folder, SilvaService):
    """Subscription Service
    """
    grok.implements(ISubscriptionService)
    default_service_identifier = 'service_subscriptions'

    meta_type = "Silva Subscription Service"
    silvaconf.icon('www/subscription_service.png')

    manage_options = (
        {'label':'Settings', 'action':'manage_settings'},
        ) + Folder.Folder.manage_options

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
        if not isValidMailAddress(emailaddress):
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
        if not isValidMailAddress(emailaddress):
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
        context = get_content_from_id(ref)
        assert context is not None, u'Invalid content'
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
        context = get_content_from_id(ref)
        assert context is not None, u'Invalid content'
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
                contentsubscribedto.absolute_url() + '/subscriptions.html'
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
        self, content, emailaddress, token, template_id, action, subscribed_content):
        ref = get_content_id(content)
        template = str(self[template_id])
        content_url = content.absolute_url()
        subscribed_url = subscribed_content.absolute_url()
        data = {}
        data['toaddress'] = emailaddress
        data['contenturl'] = content_url
        data['contenttitle'] = content.get_title().encode('utf-8')
        emailaddress = urllib.quote(emailaddress)
        data['confirmationurl'] = '%s/subscriptions.html/@@%s?%s' % (
            content_url, action, urllib.urlencode((
                ('content', ref),
                ('email', emailaddress),
                ('token', token)),))
        data['subscribedcontenturl'] = subscribed_url
        data['serviceurlforsubscribedcontent'] = subscribed_url + '/subscriptions.html'
        self._sendEmail(template, data)

    def _sendConfirmationEmail(
        self, content, emailaddress, token, template_id, action):
        ref = get_content_id(content)
        template = str(self[template_id])
        content_url = content.absolute_url()
        data = {}
        data['toaddress'] = emailaddress
        data['contenturl'] = content_url
        data['contenttitle'] = content.get_title().encode('utf-8')
        emailaddress = urllib.quote(emailaddress)
        data['confirmationurl'] = '%s/subscriptions.html/@@%s?%s' % (
            content_url, action, urllib.urlencode((
                ('content', ref),
                ('email', emailaddress),
                ('token', token)),))
        self._sendEmail(template, data)

    def _sendEmail(self, template, data):
        message = template % data
        sendmail(self, message)


InitializeClass(SubscriptionService)


class ISubscriptionFields(interface.Interface):
    email = RFC822MailAddress(
        title=_(u"Email address"),
        description=_(
            u"Enter your email on which you wish receive your notifications."),
        required=True)
    captcha = Captcha(
        title=_(u"Captcha"),
        description=_(
            u'Please retype the captcha below to verify that you are human.'),
        required=True)


class SubscriptionForm(silvaforms.PublicForm):
    grok.context(ISilvaObject)
    grok.name('subscriptions.html')
    grok.require('zope2.View')

    def update(self):
        service = queryUtility(ISubscriptionService)
        if service is None or not service.subscriptionsEnabled():
            raise NotFound(u"Subscription are not enabled.")

    @property
    def label(self):
        return _(u'subscribe / unsubscribe to ${title}',
                 mapping={'title': self.context.get_title()})
    description =_(u'Fill in your email address if you want to receive an a '
                   u'email notifications whenever a new version of this page '
                   u'or its subpages becomes available.')
    fields = silvaforms.Fields(ISubscriptionFields)

    @silvaforms.action(_(u'Subscribe'))
    def action_subscribe(self):
        data, error = self.extractData()
        if error:
            return silvaforms.FAILURE
        service = getUtility(ISubscriptionService)
        try:
            service.requestSubscription(self.context, data['email'])
        except errors.NotSubscribableError:
            self.status = _(u"You cannot subscribe to this content.")
            return silvaforms.FAILURE
        except errors.AlreadySubscribedError:
            self.status = _(u"You are already subscribed to this content.")
            return silvaforms.FAILURE
        self.status = _(u'Confirmation request for subscription '
                        u'has been emailed to ${email}.',
                        mapping={'email': data['email']})
        return silvaforms.SUCCESS

    @silvaforms.action(_(u'Unsubscribe'))
    def action_unsubscribe(self):
        data, error = self.extractData()
        if error:
            return silvaforms.FAILURE
        service = getUtility(ISubscriptionService)
        try:
            service.requestCancellation(self.context, data['email'])
        except errors.NotSubscribableError:
            self.status = _(u"You cannot subscribe to this content.")
            return silvaforms.FAILURE
        except errors.NotSubscribedError:
            self.status = _(u"You are not subscribed to this content.")
            return silvaforms.FAILURE
        self.status = _(u'Confirmation request for cancellation '
                        u'has been emailed to ${email}.',
                        mapping={'email': data['email']})
        return silvaforms.SUCCESS

    @silvaforms.action(_(u'Cancel'))
    def action_cancel(self):
        self.redirect(self.url())
        return silvaforms.SUCCESS


class SubscriptionConfirmationPage(silvaviews.Page):
    grok.context(SubscriptionForm)
    grok.name('confirm_subscription')

    template = ChameleonPageTemplate(
        filename='subscription_templates/confirmationpage.cpt')

    def __init__(self, context, request):
        super(SubscriptionConfirmationPage, self).__init__(
            context.context, request)

    def update(self, content=None, email=None, token=None):
        if content is None or email is None or token is None:
            self.status = _(u"Invalid subscription confirmation.")
            return
        service = queryUtility(ISubscriptionService)
        if service is None or not service.subscriptionsEnabled():
            self.status = _("Subscription no longer available.")
            return
        try:
            service.subscribe(content, email, token)
        except errors.SubscriptionError:
            self.status = _("Subscription failed.")
            return
        self.status = _(
            u'You have been successfully subscribed. '
            u'This means you will receive email notifications '
            u'whenever a new version of these pages becomes available.')


class SubscriptionCancellationConfirmationPage(SubscriptionConfirmationPage):
    grok.name('confirm_cancellation')

    def update(self, content=None, email=None, token=None):
        if content is None or email is None or token is None:
            self.status = _(u"Invalid confirmation.")
            return
        service = queryUtility(ISubscriptionService)
        if service is None or not service.subscriptionsEnabled():
            self.status = _(u"Subscription no longer available.")
            return
        try:
            service.unsubscribe(content, email, token)
        except errors.SubscriptionError:
            self.status = _(
                u"Something went wrong in unsubscribing from this page. "
                u"It might be that the link you followed expired.")
            return
        self.status = _(u"You have been successfully unsubscribed.")


class SubscriptionServiceManagementView(silvaforms.ZMIComposedForm):
    """Edit File Serivce.
    """
    grok.require('zope2.ViewManagementScreens')
    grok.name('manage_settings')
    grok.context(SubscriptionService)

    label = _(u"Service Subscriptions Configuration")


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

    def is_installable(self):
        if not MAILDROPHOST_AVAILABLE:
            return False
        root = self.context.get_root()
        mailhost =  getattr(root, MAILHOST_ID, None)
        return mailhost is None or mailhost.meta_type != 'Maildrop Host'

    def available(self):
        return self.status or self.is_installable()

    @silvaforms.action(
        _(u'Install'),
        available=lambda form:form.is_installable())
    def action_install(self):
        root = self.context.get_root()
        if hasattr(root, MAILHOST_ID):
            root.manage_delObjects([MAILHOST_ID,])
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
