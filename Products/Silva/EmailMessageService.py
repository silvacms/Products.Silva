# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.mail import sendmail

from five import grok
from zope import schema, interface
from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.services.base import SilvaService
from silva.translations import translate as _
from zeam.form import silva as silvaforms

logger = logging.getLogger('silva.email')


class EmailMessageService(SilvaService):
    """Simple implementation of IMemberMessageService that sends email
    messages.
    """
    grok.implements(interfaces.IMessageService)
    default_service_identifier = 'service_messages'

    meta_type = 'Silva Message Service'
    silvaconf.icon('www/message_service.png')

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
        if not hasattr(self.aq_base, '_v_messages'):
            self._v_messages = {}
        self._v_messages.setdefault(to_memberid, {}).setdefault(
            from_memberid, []).append((subject, message))

    # XXX have to open this up to the world, unfortunately..
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'send_pending_messages')
    def send_pending_messages(self):
        logger.debug("Sending pending messages...")

        get_member = self.service_members.get_member

        if not hasattr(self.aq_base, '_v_messages'):
            self._v_messages = {}

        for to_memberid, message_dict in self._v_messages.items():
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
        self._v_messages = {}

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
    _enable = schema.Bool(
        title=_(u'Enable'),
        description=_(u'Send emails when asked to.'),
        required=True)
    _fromaddr = schema.TextLine(
        title=_(u"From Address"),
        description=_(u'Email address used to send messages.'),
        required=True)


class EmailMessageSettings(silvaforms.ZMIForm):
    grok.require('zope2.ViewManagementScreens')
    grok.name('manage_settings')
    grok.context(EmailMessageService)

    label = _(u"Service Message Configuration")
    description = _(u"Configure settings for email messaging between members. "
                    u"The default MailHost service is used to send messages.")
    ignoreContent = False
    fields = silvaforms.Fields(IEmailMessageSettings)
    actions = silvaforms.Actions(silvaforms.EditAction())
