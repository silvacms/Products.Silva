# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope import interface, schema
from z3c.form import field

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.views import views as silvaviews
from silva.core.views import z3cforms as silvaz3cforms
from silva.translations import translate as _


class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to create links that show up
    in navigation or a Table of Contents. The links can be absolute or relative.
    Absolute links go to external sites while relative links go to content
    within Silva. The Link can be a hyperlink, beginning with "http://...."
    (including https, ftp, news, and mailto) or a path to Silva content. If the
    path goes to Silva content which doesn't exist, 'http://' will be placed
    before the link. This allows you to paste "www.somesite.com" into the field.
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

    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        self._url = url


InitializeClass(LinkVersion)


class ILinkFields(interface.Interface):

    url = schema.URI(
        title=_(u"url"),
        description=_(u"Link url. Links can contain anything, so it is the author's responsibility to create valid urls."),
        required=True)


class LinkAddForm(silvaz3cforms.AddForm):
    """Add form for a link.
    """

    grok.context(interfaces.ILink)
    grok.name(u'Silva Link')
    fields = field.Fields(ILinkFields)

    def create(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addLink(
            data['id'], data['title'], data['url'])


class LinkView(silvaviews.View):

    grok.context(interfaces.ILink)

    def update(self):
        if not self.is_preview:
            self.redirect(self.content.get_url())

    def render(self):
        link = self.content
        return u'Link &laquo;%s&raquo; redirects to: <a href="%s">%s</a>' % (
            link.get_title(), link.get_url(), link.get_url())
