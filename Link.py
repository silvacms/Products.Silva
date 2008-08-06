# Copyright (c) 2003-2008 Infrae. All rights reserved.
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
from Products.Silva.interfaces import IVersionedContent, IVersion
from Products.Silva.i18n import translate as _
from Products.Silva import SilvaPermissions

# XXX taken from SilvaDocument/mixedcontentsupport.py
URL_PATTERN = r'(((http|https|ftp|news)://([A-Za-z0-9%\-_]+(:[A-Za-z0-9%\-_]+)?@)?([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+)(:[0-9]+)?(/([A-Za-z0-9\-_\?!@#$%^&*/=\.]+[^\.\),;\|])?)?|(mailto:[A-Za-z0-9_\-\.]+@([A-Za-z0-9\-]+\.)+[A-Za-z0-9]+))'
_url_match = re.compile(URL_PATTERN)

from silva.core import conf

class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to include links to external
       sites &#8211; outside of Silva &#8211; in a Table of Contents. The
       content of a Link is simply a hyperlink, beginning with
       &#8220;http://....&#8221;, or https, ftp, news, and mailto.
    """)
    security = ClassSecurityInfo()

    meta_type = "Silva Link"

    implements(IVersionedContent)

    conf.icon('www/link.png')
    conf.versionClass('LinkVersion')

    def __init__(self, id):
        Link.inheritedAttribute('__init__')(self, id)
        self.id = id


InitializeClass(Link)

class LinkVersion(CatalogedVersion):
    security = ClassSecurityInfo()
    
    meta_type = "Silva Link Version"

    implements(IVersion)

    _link_type = 'absolute'
    
    def __init__(self, id, url, link_type='absolute'):
        LinkVersion.inheritedAttribute('__init__')(self, id)
        self._link_type = link_type
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
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'is_valid_url')
    def is_valid_url(self, url):
        if _url_match.match(url):
            return True
        return False
        
    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        if self._link_type == 'absolute' and not self.is_valid_url(url):
            url = 'http://' + url
        self._url = url

InitializeClass(LinkVersion)


