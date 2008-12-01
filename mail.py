# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from AccessControl import ModuleSecurityInfo
from Products.MailHost.MailHost import _encode, _mungeHeaders

module_security =  ModuleSecurityInfo('Products.Silva.helpers')

module_security.declareProtected('View', 'sendmail')
def sendmail(mh, message, mto, mfrom, subject):
    """Send a fraking mail, should work with regular Zope Mailhost,
    and MaildropHost.
    """
    messageText, mto, mfrom = _mungeHeaders(message.encode('iso8859-1'),
                                            mto, mfrom, subject)
    messageText = _encode(messageText, None)
    mh._send(mfrom, mto, messageText)

