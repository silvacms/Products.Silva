# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope import schema
from zope.traversing.browser import absoluteURL

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.conf.interfaces import ITitledContent
from silva.core.references.reference import (
    Reference, ReferenceProperty, get_content_id, get_content_from_id)
from silva.core.views import views as silvaviews
from silva.translations import translate as _

from zeam.form import silva as silvaforms


class Link(CatalogedVersionedContent):
    __doc__ = _("""A Silva Link makes it possible to create links that show up
    in navigation or a Table of Contents. The links can be absolute or relative.
    Absolute links go to external sites while relative links go to content
    within Silva.
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
        return get_content_from_id(self._target)

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
        if not isinstance(target, int):
            target = get_content_id(target)
        self._target = target

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        self._url = url


InitializeClass(LinkVersion)


class ILinkSchema(ITitledContent):

    relative = schema.Bool(
        title=_(u"relative link"),
        description=_(u"If selected, the link will to the selected "
                      u"relative content."),
        default=False,
        required=True)

    url = schema.URI(
        title=_(u"url"),
        description=_(u"If the link is not relative, "
                      u"it is the absolute link url."),
        required=False)

    target = Reference(interfaces.ISilvaObject,
        title=_("target of relative link"),
        description=_(u"If the link is relative, "
                      u"it is the target of the link."),
        required=False)

    # @interface.invariant
    # def url_validation(obj):
    #     if obj.relative and not obj.target:
    #         raise interface.Invalid(_("Relative link selected without target"))
    #     if not obj.relative and not obj.url:
    #         raise interface.Invalid(_("Absolute link selected without URL"))


class LinkAddForm(silvaforms.SMIAddForm):
    """Add form for a link.
    """
    grok.context(interfaces.ILink)
    grok.name(u'Silva Link')

    fields = silvaforms.Fields(ILinkSchema)
    description = Link.__doc__



class LinkEditForm(silvaforms.SMIEditForm):
    """Edit form for a link.
    """
    grok.context(interfaces.ILink)

    fields = silvaforms.Fields(ILinkSchema).omit('id')


class LinkView(silvaviews.View):
    """Render a link.
    """
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


