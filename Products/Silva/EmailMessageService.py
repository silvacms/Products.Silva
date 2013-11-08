# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import threading
import logging

from zope.component import queryUtility, getUtility
from five import grok
from zope import schema, interface

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.mail import sendmail

import transaction
from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.interfaces import ISilvaConfigurableService
from silva.core.services.interfaces import IMemberService
from silva.core.services.base import SilvaService
from silva.translations import translate as _
from zeam.form import silva as silvaforms

logger = logging.getLogger('silva.email')


# XXX This should be updated to use silva.core.services.delayed


class EmailQueueSavepoint(object):
    grok.implements(IDataManagerSavepoint)

    def __init__(self, email_queue_transaction):
        self.email_queue_transaction = email_queue_transaction

    def rollback(self):
        self.email_queue_transaction._rollback_queue()


class EmailQueueTransaction(threading.local):
    """ Email queue transaction.
    """
    grok.implements(ISavepointDataManager)

    _followed = False
    _active = True

    def __init__(self, manager):
        self.transaction_manager = manager
        self._reset()

    def activate(self):
        if not self._active:
            self._follow()
            self._active = True

    def deactivate(self):
        self._active = False

    def clear(self):
        self._reset()

    def _reset(self):
        self._current_queue = {}
        self._queues = [self._current_queue]

    def _start_queue(self):
        if self._current_queue:
            self._current_queue = {}
            self._queues.append(self._current_queue)

    def _rollback_queue(self):
        if self._current_queue:
            self._queues.pop()
            self._current_queue = {}
            self._queues.append(self._current_queue)

    def _follow(self):
        if not self._followed:
            service = queryUtility(interfaces.IMessageService)
            if service is None:
                return
            transaction = self.transaction_manager.get()
            transaction.join(self)
            transaction.addBeforeCommitHook(service.send_pending_messages)
            self._followed = True

    def enqueue_email(self, from_memberid, to_memberid, subject, message):
        if self._active:
            self._follow()
            self._current_queue.setdefault(to_memberid, {}).setdefault(
                from_memberid, []).append((subject, message))

    def __iter__(self):
        members = set()
        for queue in self._queues:
            members |= set(queue.iterkeys())
        for member in members:
            message_dict = {}
            for queue in self._queues:
                messages = queue.get(member)
                if messages is not None:
                    for from_member, message_list in messages.iteritems():
                        message_dict.setdefault(
                            from_member, []).extend(message_list)
            yield (member, message_dict)

    def sortKey(self):
        # This should let us appear after the Data.fs ...
        return 'z' * 50

    def savepoint(self):
        self._start_queue()
        return EmailQueueSavepoint(self)

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def abort(self, transaction):
        self._reset()

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        pass

    def tpc_abort(self, transaction):
        pass


email_queue = EmailQueueTransaction(transaction.manager)


@grok.subscribe(interfaces.IUpgradeStartedEvent)
def deactivate_before_upgrade(event):
    email_queue.deactivate()

@grok.subscribe(interfaces.IUpgradeFinishedEvent)
def activate_after_upgrader(event):
    email_queue.activate()


class EmailMessageService(SilvaService):
    """Simple implementation of IMemberMessageService that sends email
    messages.
    """
    meta_type = 'Silva Message Service'
    grok.implements(interfaces.IMessageService, ISilvaConfigurableService)
    grok.name('service_messages')
    silvaconf.default_service()
    silvaconf.icon('icons/service_message.png')

    manage_options = (
        {'label':'Settings', 'action':'manage_settings'},
        ) + SilvaService.manage_options

    security = ClassSecurityInfo()

    _fromaddr = None
    _enabled = False

    # XXX these security settings are not the right thing.. perhaps
    # create a new permission?
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'send_message')
    def send_message(self, from_memberid, to_memberid, subject, message):
        email_queue.enqueue_email(
            from_memberid, to_memberid, subject, message)

    security.declarePublic('send_pending_messages')
    def send_pending_messages(self):
        logger.debug("Sending pending messages...")

        service_members = getUtility(IMemberService)
        get_member = service_members.get_member

        for to_memberid, message_dict in email_queue:
            to_member = get_member(to_memberid)
            if to_member is None:
                # XXX get_member should return a NoneMember, not just None
                # in case the member cannot be found. Apparently sometimes
                # it *does* return.
                logger.debug("no member found for: %s" % to_memberid)
                continue
            to_email = to_member.email()
            if to_email is None:
                logger.debug("no email for: %s" % to_memberid)
                continue
            lines = []
            # XXX usually all messages have the same subject yet,
            # but this can be assumed here per se.
            common_subject=None
            reply_to = {}
            for from_memberid, messages in message_dict.items():
                logger.debug("From memberid: %s " % from_memberid)
                from_member = get_member(from_memberid)
                if from_member is None:
                    # XXX get_member should return a NoneMember, not just None
                    # in case the member cannot be found. Apparently sometimes
                    # it *does* return.
                    logger.debug("no member found for: %s" % to_memberid)
                    continue
                from_email = from_member.email()
                if from_email is not None:
                    reply_to[from_email] = 1
                    lines.append("Message from: %s (email: %s)" %
                                 (from_memberid, from_email))
                else:
                    lines.append("Message from: %s (no email available)" %
                                 from_memberid)
                for subject, message in messages:
                    lines.append(subject)
                    lines.append('')
                    lines.append(message)
                    lines.append('')
                    if common_subject is None:
                        common_subject = subject
                    else:
                        if common_subject != subject:
                            # XXX this is very stupid, but what else?
                            # maybe leave empty?
                            common_subject = 'Notification on status change'

            text = '\n'.join(lines)
            header = {}
            if common_subject is not None:
                header['Subject'] = common_subject
            if reply_to:
                header['Reply-To'] = ', '.join(reply_to.keys())
                # XXX set from header ?
            self._send_email(to_email, text, header=header)

        # XXX if above raises exception: mail queue is not flushed
        # as this line is not reached. bug or feature ?
        email_queue.clear()

    # ACCESSORS
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'fromaddr')
    def fromaddr(self):
        """return self._fromaddr"""
        return self._fromaddr

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'send_email_enabled')
    def send_email_enabled(self):
        return self._enabled

    def _send_email(self, toaddr, msg, header={}):
        if not self._enabled:
            return
        header['To'] = toaddr
        if not header.has_key('From'):
            header['From'] = self._fromaddr
        if not header.has_key('Sender'):
            header['Sender'] = self._fromaddr
        header['Content-Type'] = 'text/plain; charset=UTF-8'

        msg_lines = [ '%s: %s' % (k, v) for k, v in header.items() ]
        msg_lines.append('')
        msg_lines.append(msg)
        msg = '\r\n'.join(msg_lines)
        if isinstance(msg, unicode):
            msg = msg.encode('UTF-8')

        # Send the email using the mailhost
        sendmail(self, msg, toaddr, self._fromaddr)

InitializeClass(EmailMessageService)


class IEmailMessageSettings(interface.Interface):
    _enabled = schema.Bool(
        title=_(u'Enable'),
        description=_(u'Send emails when asked to.'),
        required=True)
    _fromaddr = schema.TextLine(
        title=_(u"From Address"),
        description=_(u'Email address used to send messages.'),
        required=True)


class EmailMessageSettings(silvaforms.ZMIForm):
    grok.context(EmailMessageService)
    grok.require('zope2.ViewManagementScreens')
    grok.name('manage_settings')

    label = _(u"Messaging configuration")
    description = _(u"Configure settings for email messaging between members. "
                    u"The default MailHost service is used to send messages.")
    ignoreContent = False
    fields = silvaforms.Fields(IEmailMessageSettings)
    actions = silvaforms.Actions(silvaforms.EditAction())


class EmailMessageConfiguration(silvaforms.ConfigurationForm):
    grok.context(EmailMessageService)

    label = _(u"Messaging configuration")
    description = _(u"Configure settings for email messaging between members. "
                    u"The default MailHost service is used to send messages.")
    fields = silvaforms.Fields(IEmailMessageSettings)
    actions = silvaforms.Actions(
        silvaforms.CancelConfigurationAction(),
        silvaforms.EditAction())
