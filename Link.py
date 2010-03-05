# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope import interface, schema
from zope.traversing.browser import absoluteURL
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
from silva.core.references.reference import Reference, ReferenceProperty
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

    _url = None
    _relative = False
    _target = ReferenceProperty(name=u'link')

    security.declareProtected(SilvaPermissions.View, 'get_relative')
    def get_relative(self):
        return self._relative

    security.declareProtected(SilvaPermissions.View, 'get_target')
    def get_target(self):
        return self._target

    security.declareProtected(SilvaPermissions.View, 'get_url')
    def get_url(self):
        return self._url

    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_relative')
    def set_relative(self, relative):
        self._relative = relative

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_target')
    def set_target(self, target):
        self._target = target

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        self._url = url


InitializeClass(LinkVersion)


class ILinkSchema(interface.Interface):

    relative = schema.Bool(
        title=_(u"relative link"),
        default=False,
        required=True)

    url = schema.URI(
        title=_(u"url"),
        description=_(u"Link url"),
        required=False)

    target = Reference(
        title=_("target of relative link"),
        required=False)


class LinkAddForm(silvaz3cforms.AddForm):
    """Add form for a link.
    """
    grok.context(interfaces.ILink)
    grok.name(u'Silva Link')
    fields = field.Fields(ILinkSchema)

    def create(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addLink(
            data['id'], data['title'],
            url=data['url'], relative=data['relative'], target=data['target'])


class LinkEditForm(silvaz3cforms.EditForm):
    """Edit form for a link.
    """
    grok.context(interfaces.ILink)
    fields = field.Fields(ILinkSchema)


class LinkView(silvaviews.View):

    grok.context(interfaces.ILink)

    def update(self):
        self.url = None
        if self.content.get_relative():
            self.url = absoluteURL(self.content.get_target(), self.request)
        else:
            self.url = self.content.get_url()
        if not self.is_preview:
            self.redirect(self.url)

    def render(self):
        return u'Link &laquo;%s&raquo; redirects to: <a href="%s">%s</a>' % (
            self.content.get_title(), self.url, self.url)
