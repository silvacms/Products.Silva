# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

# Zope 3
from five import grok
from zope import interface, schema
from z3c.form import field

# Zope 2
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva.i18n import translate as _
from Products.Silva import SilvaPermissions

from silva.core.views import views as silvaviews
from silva.core.views import z3cforms as silvaz3cforms
from silva.core import interfaces
from silva.core import conf as silvaconf


class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to include links to external
       sites &#8211; outside of Silva &#8211; in a Table of Contents. The
       content of a Link is simply a hyperlink, beginning with
       &#8220;http://....&#8221;, or https, ftp, news, and mailto.
    """)

    meta_type = "Silva Link"

    grok.implements(interfaces.ILink)
    silvaconf.icon('www/link.png')
    silvaconf.versionClass('LinkVersion')


class LinkVersion(CatalogedVersion):
    security = ClassSecurityInfo()

    meta_type = "Silva Link Version"

    grok.implements(interfaces.ILinkVersion)

    def __init__(self, id, url):
        super(LinkVersion, self).__init__(id)
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


class ILinkAddFields(interface.Interface):

    url = schema.URI(
        title=_(u"url"),
        description=_(u"Link url. Links can contain anything, so it is the author's responsibility to create valid urls."),
        required=True)


class LinkAddForm(silvaz3cforms.AddForm):
    """Add form for a file.
    """

    silvaconf.context(interfaces.ILink)
    silvaconf.name(u'Silva Link')
    fields = field.Fields(ILinkAddFields)

    def create(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addLink(
            data['id'], data['title'], data['url'])
