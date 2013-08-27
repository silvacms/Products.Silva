
# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zope import schema, interface
from zope.traversing.browser import absoluteURL
from zope.component import getUtility

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from App.class_init import InitializeClass

# Silva
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.conf.interfaces import ITitledContent
from silva.core.references.reference import Reference, get_content_id
from silva.core.references.interfaces import IReferenceService
from silva.core.views import views as silvaviews
from silva.translations import translate as _

from zeam.form import silva as silvaforms


class Link(VersionedContent):
    __doc__ = _("""A Silva Link makes it possible to create links that show up
    in navigation or a Table of Contents. The links can be absolute or relative.
    Absolute links go to external sites while relative links go to content
    within Silva.
    """)

    meta_type = "Silva Link"

    grok.implements(interfaces.ILink)
    silvaconf.icon('icons/link.png')
    silvaconf.versionClass('LinkVersion')


class LinkVersion(Version):
    security = ClassSecurityInfo()

    meta_type = "Silva Link Version"

    grok.implements(interfaces.ILinkVersion)

    _url = None
    _relative = False

    security.declareProtected(SilvaPermissions.View, 'get_relative')
    def get_relative(self):
        return self._relative

    security.declareProtected(SilvaPermissions.View, 'get_target')
    def get_target(self):
        if self._relative:
            service = getUtility(IReferenceService)
            reference = service.get_reference(
                aq_inner(self), name=u'link')
            if reference is not None:
                return reference.target
        return None

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
        service = getUtility(IReferenceService)
        if not isinstance(target, int):
            target = get_content_id(target)
        if target:
            reference = service.get_reference(
                aq_inner(self), name=u'link', add=True)
            reference.set_target_id(target)
        else:
            reference = service.delete_reference(
                aq_inner(self), name=u'link')

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_url')
    def set_url(self, url):
        self._url = url


InitializeClass(LinkVersion)


class ILinkSchema(ITitledContent):

    url = schema.URI(
        title=_(u"URL"),
        description=_(
            u"If the link goes to an external resource, fill in the "
            u"location, including the protocol, e.g. 'http://'."),
        required=False)

    relative = schema.Bool(
        title=_(u"Relative link"),
        description=_(
            u"If the link goes to an internal item in Silva, put a checkmark "
            u"here and lookup the target below."),
        default=False,
        required=True)

    target = Reference(interfaces.ISilvaObject,
        title=_(u"Target of relative link"),
        description=_(
            u"Make a reference to an internal item by looking it up."),
        required=False)

    @interface.invariant
    def url_validation(content):
        if content.relative and not content.target:
            raise interface.Invalid(
                _(u"Relative link selected without target."))
        if not content.relative and not content.url:
            raise interface.Invalid(
                _(u"Absolute link selected without URL. "
                  u"If the link goes to an internal item in Silva, "
                  u"put a checkmark in the relative link field."))


class LinkAddForm(silvaforms.SMIAddForm):
    """Add form for a link.
    """
    grok.context(interfaces.ILink)
    grok.name(u'Silva Link')

    fields = silvaforms.Fields(ILinkSchema)
    fields['target'].referenceNotSetLabel = _(
        u"Click the Lookup button to select an item to refer to.")


class LinkEditForm(silvaforms.SMIEditForm):
    """Edit form for a link.
    """
    grok.context(interfaces.ILink)

    fields = silvaforms.Fields(ILinkSchema).omit('id')
    fields['target'].referenceNotSetLabel = _(
        u"Click the Lookup button to select an item to refer to.")


class LinkView(silvaviews.View):
    """Render a link.
    """
    grok.context(interfaces.ILink)

    def update(self):
        self.url = None
        if self.content.get_relative():
            target = self.content.get_target()
            if target is not None:
                self.url = absoluteURL(target, self.request)
        else:
            self.url = self.content.get_url()
        if not self.is_preview and self.url is not None:
            self.response.redirect(self.url)
