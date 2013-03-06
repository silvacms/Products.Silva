# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from five import grok
from zope.component import queryUtility

from AccessControl import getSecurityManager
from DateTime import DateTime

from silva.core import interfaces
from silva.core.interfaces import events


logger = logging.getLogger('silva.core.message')


def format_date(dt):
    return "%02d %s %04d %02d:%02d" % (
        dt.day(), dt.aMonth().lower(), dt.year(), dt.hour(), dt.minute())


def send_message_to_editors(target, from_userid, subject, text):
    message_service = queryUtility(interfaces.IMessageService)
    if message_service is None:
        logger.info(u'Message service missing skipping message.')
        return
    # find out some information about the object and add it to the
    # message
    text = "Object: %s\n%s/edit/tab_preview\n%s" % (
        target.get_title_editable(),
        target.absolute_url(), text)
    # XXX this may not get the right people, but what does?
    current = target.get_silva_object().aq_inner
    recipients = []
    while True:
        auth = interfaces.IAuthorizationManager(current)
        authorizations = auth.get_defined_authorizations(
            dont_acquire=True)
        for identifier, authorization in authorizations.iteritems():
            if authorization.role == 'ChiefEditor':
                recipients.append(identifier)

        if not interfaces.IRoot.providedBy(current):
            current = current.aq_parent
            continue
        break
    for userid in recipients:
        if userid==from_userid:
            continue
        message_service.send_message(
            from_userid, userid, subject, text)

def send_message(target, from_userid, to_userid, subject, text):
    if from_userid == to_userid:
        return
    message_service = queryUtility(interfaces.IMessageService)
    if message_service is None:
        logger.info(u'Message service missing skipping message.')
        return
    # find out some information about the object and add it to the
    # message
    text = "Object: %s\n%s/edit/tab_preview\n%s" % (
        target.get_title_editable(),
        target.absolute_url(), text)
    message_service.send_message(from_userid, to_userid, subject, text)

@grok.subscribe(interfaces.IVersion, events.IContentApprovedEvent)
def send_messages_approved(content, event):
    if not len(event.status.messages) > 1:
        return
    message = event.status.messages[-2]

    message_service = queryUtility(interfaces.IMessageService)
    if message_service is None:
        logger.info(u'Message service missing skipping message.')
        return

    now = DateTime()
    manager = interfaces.IVersionManager(content)
    publication_datetime = manager.get_publication_datetime()
    expiration_datetime = manager.get_expiration_datetime()

    if publication_datetime > now:
        publication_date_str = 'The version will be published at %s\n' % \
                              format_date(publication_datetime)
    else:
        publication_date_str="The version has been published right now.\n"
    if expiration_datetime is None:
        expiration_date_str=''
    else:
        expiration_date_str = 'The version will expire at %s\n' % \
                              format_date(expiration_datetime)
    editor = getSecurityManager().getUser().getId()
    text = u"\nVersion was approved for publication by %s.\n%s%s" % \
            (editor, publication_date_str, expiration_date_str)

    message_service.send_message(
        editor, message.user_id, "Version approved", text)

@grok.subscribe(interfaces.IVersion, events.IContentUnApprovedEvent)
def send_messages_unapproved(content, event):
    # send messages to editor
    author = getSecurityManager().getUser().getId()
    text = u"\nVersion was unapproved by %s." % author
    send_message_to_editors(content, author, 'Unapproved', text)

    if len(event.status.messages) > 1:
        message = event.status.messages[-2]
        send_message(content, author, message.user_id, 'Unapproved', text)

@grok.subscribe(interfaces.IVersion,
                events.IContentRequestApprovalEvent)
def send_messages_request_approval(content, event):
    assert len(event.status.messages) >= 1, \
        u"Event should not have been triggered"
    message = event.status.messages[-1]

    manager = interfaces.IVersionManager(content)
    publication_datetime = manager.get_publication_datetime()
    expiration_datetime = manager.get_expiration_datetime()

    if publication_datetime is None:
        publication_date_str=''
    else:
        publication_date_str = \
                 'The version has a proposed publication date of %s\n' % \
                 format_date(publication_datetime)
    if expiration_datetime is None:
        expiration_date_str=''
    else:
        expiration_date_str = \
           'The version has a proposed expiration date of %s\n' % \
           format_date(expiration_datetime)
    # send messages
    text = u"\nApproval was requested by %s.\n%s%s\nMessage:\n%s" % \
            (message.user_id,
             publication_date_str,
             expiration_date_str,
             message.message)

    send_message_to_editors(
        content, message.user_id, 'Approval requested', text)
    last_author = content.get_last_author_info().userid()
    send_message(
        content, message.user_id, last_author,
        'Approval requested', text)

@grok.subscribe(interfaces.IVersion,
                events.IContentApprovalRequestWithdrawnEvent)
def send_messages_content_approval_request_withdrawn(content, event):
    assert len(event.status.messages) >= 2, \
        u"Event should not have been triggered"
    message = event.status.messages[-1]
    original_requester = event.status.messages[-2].user_id

    # send messages
    text = u"\nRequest for approval was withdrawn by %s.\nMessage:\n%s" \
           % (message.user_id, message.message)
    send_message_to_editors(
        content, message.user_id,
        'Approval withdrawn by author', text)
    send_message(
        content, message.user_id, original_requester,
        'Approval withdrawn by author', text)

@grok.subscribe(interfaces.IVersion,
                events.IContentApprovalRequestRefusedEvent)
def send_messages_content_approval_request_refused(content, event):
    assert len(event.status.messages) >= 2, \
        u"Event should not have been triggered"
    message = event.status.messages[-1]
    original_requester = event.status.messages[-2].user_id

    text = u"Request for approval was rejected by %s.\nMessage:\n%s" \
           % (message.user_id, message.message)
    send_message(content, message.user_id, original_requester,
        "Approval rejected by editor", text)


