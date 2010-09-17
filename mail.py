# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging
from smtplib import SMTPException

# Zope
from AccessControl import ModuleSecurityInfo
from Products.MailHost.MailHost import _encode, _mungeHeaders
from Products.Silva import MAILHOST_ID

logger = logging.getLogger('silva.email')

module_security =  ModuleSecurityInfo('Products.Silva.helpers')

module_security.declareProtected('Use mailhost services', 'sendmail')
def sendmail(context, message, mto=None, mfrom=None, subject=None):
    """Send a fraking mail, should work with regular Zope Mailhost,
    and MaildropHost.
    """

    mh = getattr(context.get_root(), MAILHOST_ID)
    messageText, mto, mfrom = _mungeHeaders(message, mto, mfrom, subject)
    messageText = _encode(messageText, None)
    try:
        mh._send(mfrom, mto, messageText)
    except SMTPException as error:
        logger.error('Error sending email from %s to %s: %s' % (
                mfrom, mto, str(error)))
