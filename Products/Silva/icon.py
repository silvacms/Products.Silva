# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.annotation.interfaces import IAnnotations

# Silva
from silva.core import interfaces
from silva.core.views.interfaces import IVirtualSite


class SilvaIcons(grok.DirectoryResource):
    # This export the globals directory using Zope 3 technology.
    grok.path('icons')
    grok.name('silva.icons')


class IconRegistry(object):
    grok.implements(interfaces.IIconRegistry)

    def __init__(self):
        self.__icons = {}

    def getIcon(self, content):
        if interfaces.IGhost.providedBy(content):
            version = content.getLastVersion()
            if version.get_link_status() == version.LINK_OK:
                kind = 'link_ok'
            else:
                kind = 'link_broken'
            identifier = ('ghost', kind)
        elif interfaces.IGhostFolder.providedBy(content):
            if content.get_link_status() == content.LINK_OK:
                if interfaces.IPublication.providedBy(content):
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
            if interfaces.IAuthorization.providedBy(content):
                content = content.source
            meta_type = getattr(content, 'meta_type', None)
            if meta_type is None:
                raise ValueError(u"No icon for unknown object %r" % content)
            identifier = ('meta_type', meta_type)
        return self.getIconByIdentifier(identifier)

    def getIconByIdentifier(self, identifier):
        icon = self.__icons.get(identifier, None)
        if icon is None:
            raise ValueError(u"No icon for %r" % repr(identifier))
        return icon

    def registerIcon(self, identifier, icon_name):
        """Register an icon.

        NOTE: this will overwrite previous icon declarations
        """
        self.__icons[identifier] = icon_name


registry = IconRegistry()

def _get_icon_base_url(request):
    annotations = IAnnotations(request)
    base_url = annotations.get('silva.icon.baseurl')
    if base_url is None:
        site = IVirtualSite(request)
        base_url = site.get_root_url()
        annotations['silva.icon.baseurl'] = base_url
    return base_url


def get_icon_url(content, request):
    """Return a content icon URL.
    """
    try:
        icon = registry.getIcon(content)
    except ValueError:
        icon = 'globals/silvageneric.gif'
    return "/".join(( _get_icon_base_url(request), icon,))


def get_meta_type_icon(meta_type):
    """Return a content icon from its meta_type.
    """
    try:
        return registry.getIconByIdentifier(('meta_type', meta_type))
    except ValueError:
        return 'globals/silvageneric.gif'

def get_meta_type_icon_url(meta_type, request):
    """Return a content icon URL from its meta_type.
    """
    return "/".join(
        (_get_icon_base_url(request), get_meta_type_icon(meta_type)))
