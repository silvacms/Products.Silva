# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

# Zope 3
from zope.interface import implements

# Zope 2
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from silva.core.interfaces import IVersionedContent, IVersion
from Products.Silva.i18n import translate as _
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf

class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to include links to external
       sites &#8211; outside of Silva &#8211; in a Table of Contents. The
       content of a Link is simply a hyperlink, beginning with
       &#8220;http://....&#8221;, or https, ftp, news, and mailto.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Link"

    implements(IVersionedContent)

    silvaconf.icon('www/link.png')
    silvaconf.versionClass('LinkVersion')

    def __init__(self, id):
        Link.inheritedAttribute('__init__')(self, id)
        self.id = id


InitializeClass(Link)

class LinkVersion(CatalogedVersion):
    security = ClassSecurityInfo()
    
    meta_type = "Silva Link Version"

    implements(IVersion)

    def __init__(self, id, url):
        LinkVersion.inheritedAttribute('__init__')(self, id)
        self.set_url(url)
        
    security.declareProtected(SilvaPermissions.View, 'get_url')
    def get_url(self):
        return self._url

    security.declareProtected(SilvaPermissions.View, 'redirect')
    def redirect(self, view_type='public'):
        request = self.REQUEST
        response = request.RESPONSE
        if (request['HTTP_USER_AGENT'].startswith('Mozilla/4.77') or
            request['HTTP_USER_AGENT'].find('Opera') > -1):
            return ('<html><head><META HTTP-EQUIV="refresh" '
                    'CONTENT="0; URL=%s"></head><body bgcolor="#FFFFFF">'
                    '</body></html>') % self._url
        else:
            response.redirect(self._url)
            return ""
        
    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        self._url = url

InitializeClass(LinkVersion)


