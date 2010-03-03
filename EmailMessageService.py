# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import logging
import smtplib
import string

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit

# other products
from Products.Formulator.Form import ZMIForm
from Products.Formulator.Errors import FormValidationError
from Products.Formulator import StandardFields

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.services.base import SilvaService
from silva.translations import translate as _


logger = logging.getLogger('silva.email')


class EmailMessageService(SilvaService):
    """Simple implementation of IMemberMessageService that sends email
    messages.
    """

    title = 'Silva Message Service'
    meta_type = 'Silva Message Service'

    security = ClassSecurityInfo()

    implements(interfaces.IMessageService)

    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SilvaService.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/emailMessageServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    silvaconf.icon('www/message_service.png')
    silvaconf.factory('manage_addEmailMessageServiceForm')
    silvaconf.factory('manage_addEmailMessageService')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._host = None
        self._port = 25
        self._fromaddr = None
        self._send_email_enabled = 0
        self._debug = 0

        edit_form = ZMIForm('edit', 'Edit')

        host = StandardFields.StringField(
            'host',
            title="Host",
            required=1,
            display_width=20)
        port = StandardFields.IntegerField(
            'port',
            title="Port",
            required=1,
            display_width=20)
        fromaddr = StandardFields.EmailField(
            'fromaddr',
            title="From address",
            required=1,
            display_width=20)
        send_email_enabled = StandardFields.CheckBoxField(
            'send_email_enabled',
            title="Actually send email",
            required=0,
            default=0)
        debug = StandardFields.CheckBoxField(
            'debug',
            title="Debug mode",
            required=0,
            default=0)

        for field in [host, port, fromaddr, send_email_enabled, debug]:
            edit_form._setObject(field.id, field)
        self.edit_form = edit_form

    # edit_form is a full-fledged zope 2 object so should not need
    # a security declaration. Removing to prevent warnings.
    #security.declareProtected(SilvaPermissions.ViewManagementScreens,
    #                          'edit_form')

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'manage_edit')
    def manage_edit(self, REQUEST):
        """manage method to update data"""
        try:
            result = self.edit_form.validate_all(REQUEST)
        except FormValidationError, e:
            # XXX i18n - not sure if this isn't used for anything
            messages = [_("Validation error(s)")]
            # loop through all error texts and generate messages for it
            for error in e.errors:
                messages.append("%s: %s" % (error.field.get_value('title'),
                                            error.error_text))
            # join them all together in a big message
            message = string.join(messages, "<br />")
            # return to manage_editForm showing this failure message
            return self.manage_editForm(self, REQUEST,
                                        manage_tabs_message=message)

        for key, value in result.items():
            setattr(self, '_' + key, value)
        return self.manage_main(manage_tabs_message=_("Changed settings."))

    # XXX these security settings are not the right thing.. perhaps
    # create a new permission?
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'send_message')
    def send_message(self, from_memberid, to_memberid, subject, message):
        if not hasattr(self.aq_base, '_v_messages'):
            self._v_messages = {}
        self._v_messages.setdefault(to_memberid, {}).setdefault(
            from_memberid, []).append((subject, message))

    # XXX have to open this up to the world, unfortunately..
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'send_pending_messages')
    def send_pending_messages(self):
        self._debug_log("Sending pending messages...")

        get_member = self.service_members.get_member

        if not hasattr(self.aq_base, '_v_messages'):
            self._v_messages = {}

        for to_memberid, message_dict in self._v_messages.items():
            to_member = get_member(to_memberid)
            if to_member is None:
                # XXX get_member should return a NoneMember, not just None
                # in case the member cannot be found. Apparently sometimes
                # it *does* return.
                self._debug_log("no member found for: %s" % to_memberid)
                continue
            to_email = to_member.email()
            if to_email is None:
                self._debug_log("no email for: %s" % to_memberid)
                continue
            lines = []
            # XXX usually all messages have the same subject yet,
            # but this can be assumed here per se.
            common_subject=None
            reply_to = {}
            for from_memberid, messages in message_dict.items():
                self._debug_log("From memberid: %s " % from_memberid)
                from_member = get_member(from_memberid)
                if from_member is None:
                    # XXX get_member should return a NoneMember, not just None
                    # in case the member cannot be found. Apparently sometimes
                    # it *does* return.
                    self._debug_log("no member found for: %s" % to_memberid)
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

    def _debug_log(self, message):
        """ simple helper for logging """
        # XXX logger.debug should be used directly instead of this
        if self._debug:
            logger.debug(message)

    # ACCESSORS
    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'server')
    def server(self):
        """Returns (host, port)"""
        return (self._host, self._port)

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'host')
    def host(self):
        """return self._host"""
        return self._host

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'port')
    def port(self):
        """return self._port"""
        return self._port

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'fromaddr')
    def fromaddr(self):
        """return self._fromaddr"""
        return self._fromaddr

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'debug')
    def debug(self):
        return self._debug

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'send_email_enabled')
    def send_email_enabled(self):
        return self._send_email_enabled

    def _send_email(self, toaddr, msg, header={}):
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
        if type(msg) == type(u''):
            msg = msg.encode('UTF-8')
        self._debug_log(msg)
        if self._send_email_enabled:
            try:
                server = smtplib.SMTP(self._host, self._port)
                failures = server.sendmail(self._fromaddr, [toaddr], msg)
                server.quit()
                if failures:
                    # next line raises KeyError if toaddr is no key
                    # in failures -- however this should not happen
                    error = failures[toaddr]
                    logger.error(
                        'could not send mail to %s, error[%s]: %s' % (
                            toaddr, error[0], error[1]))

            except smtplib.SMTPException, error:
                # if e.g. connection is refused, this raises another
                # kind of exception but smtplib.SMTPException
                logger.error('sending mail failed %s' % repr(error))


InitializeClass(EmailMessageService)

manage_addEmailMessageServiceForm = PageTemplateFile(
    "www/serviceEmailMessageServiceAdd", globals(),
    __name__='manage_addEmailMessageServiceForm')

def manage_addEmailMessageService(self, id, title='', REQUEST=None):
    """Add member message service."""
    object = EmailMessageService(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
