# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.cachedescriptors.property import CachedProperty
from zope.publisher.interfaces.browser import IBrowserRequest

# Silva
from silva.core import interfaces
from silva.core.views.interfaces import IVirtualSite
from silva.core.interfaces.adapters import IIconResolver


class SilvaIcons(grok.DirectoryResource):
    # This export the globals directory using Zope 3 technology.
    grok.path('icons')
    grok.name('silva.icons')


class IconRegistry(object):
    grok.implements(interfaces.IIconRegistry)

    def __init__(self):
        self._icons = {}

    def get_icon(self, content):
        if interfaces.IGhost.providedBy(content):
            identifier = ('ghost', 'link_ok')
        elif interfaces.IGhostFolder.providedBy(content):
            if content.get_link_status() is None:
                if interfaces.IPublication.providedBy(content.get_target()):
                    kind = 'publication'
                else:
                    kind = 'folder'
            else:
                kind = 'link_broken'
            identifier = ('ghostfolder', kind)
        elif interfaces.IFile.providedBy(content):
            identifier = ('mime_type', content.get_mime_type())
        elif interfaces.ISilvaObject.providedBy(content):
            identifier = ('meta_type', content.meta_type)
        else:
            if content is None:
                return '++static++/silva.icons/missing.png'
            if interfaces.IAuthorization.providedBy(content):
                content = content.source
            meta_type = getattr(content, 'meta_type', None)
            if meta_type is None:
                raise ValueError(u"No icon for unknown object %r" % content)
            identifier = ('meta_type', meta_type)
        return self.get_icon_by_identifier(identifier)

    def get_icon_by_identifier(self, identifier):
        icon = self._icons.get(identifier, None)
        if icon is None:
            raise ValueError(u"No icon for %r" % repr(identifier))
        return icon

    def register(self, identifier, icon_name):
        """Register an icon.

        NOTE: this will overwrite previous icon declarations
        """
        self._icons[identifier] = icon_name


registry = IconRegistry()


class IconResolver(grok.Adapter):
    grok.context(IBrowserRequest)
    grok.implements(IIconResolver)

    default = '++static++/silva.icons/silvageneric.gif'

    def __init__(self, request):
        self.request = request

    @CachedProperty
    def _base_url(self):
        site = IVirtualSite(self.request)
        return site.get_root_url()

    def get_tag(self, content=None, identifier=None):
        if content is not None:
            url = self.get_content_url(content)
            alt = getattr(content, 'meta_type', None)
        else:
            url = self.get_identifier_url(identifier)
            alt = identifier
        return """<img height="16" width="16" src="%s" alt="%s" />""" % (
            url, alt)

    def get_identifier(self, identifier):
        try:
            return registry.get_icon_by_identifier(('meta_type', identifier))
        except ValueError:
            return self.default

    def get_content(self, content):
        try:
            return registry.get_icon(content)
        except ValueError:
            return self.default

    def get_content_url(self, content):
        """Return a content icon URL.
        """
        return "/".join((self._base_url, self.get_content(content),))

    def get_identifier_url(self, identifier):
        """Return a URL out of a identifier.
        """
        return "/".join((self._base_url, self.get_identifier(identifier),))
