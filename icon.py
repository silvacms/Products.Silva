# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""Silva icon registry"""

from five import grok
from zope.annotation.interfaces import IAnnotations

# Silva
from silva.core.interfaces import (
    IFile, ISilvaObject, IGhost, IGhostFolder, IIconRegistry, IPublication)
from silva.core.views.interfaces import IVirtualSite


class SilvaIcons(grok.DirectoryResource):
    # This export the globals directory using Zope 3 technology.
    grok.path('icons')
    grok.name('silva.icons')


class IconRegistry(object):
    grok.implements(IIconRegistry)

    def __init__(self):
        self._icon_mapping = {}

    def getIcon(self, content):
        if IGhost.providedBy(content):
            version = content.getLastVersion()
            if version.get_link_status() == version.LINK_OK:
                kind = 'link_ok'
            else:
                kind = 'link_broken'
            identifier = ('ghost', kind)
        elif IGhostFolder.providedBy(content):
            if content.get_link_status() == content.LINK_OK:
                if IPublication.providedBy(content):
                    kind = 'publication'
                else:
                    kind = 'folder'
            else:
                kind = 'link_broken'
            identifier = ('ghostfolder', kind)
        elif IFile.providedBy(content):
            identifier = ('mime_type', content.get_mime_type())
        elif ISilvaObject.providedBy(content):
            identifier = ('meta_type', content.meta_type)
        else:
            meta_type = getattr(content, 'meta_type', None)
            if meta_type is None:
                raise ValueError, "Icon not found"
            identifier = ('meta_type', meta_type)
        return self.getIconByIdentifier(identifier)

    def getIconByIdentifier(self, identifier):
        icon = self._icon_mapping.get(identifier, None)
        if icon is None:
            raise ValueError, "No icon for %s" % repr(identifier)
        return icon

    def registerIcon(self, identifier, icon_name):
        """Register an icon.

        NOTE: this will overwrite previous icon declarations
        """
        self._icon_mapping[identifier] = icon_name


registry = IconRegistry()

def get_icon_url(content, request):
    annotations = IAnnotations(request)
    base_url = annotations.get('silva.icon.baseurl')
    if base_url is None:
        site = IVirtualSite(request)
        base_url = site.get_root_url()
        annotations['silva.icon.baseurl'] = base_url
    try:
        icon = registry.getIcon(content)
    except ValueError:
        icon = 'globals/silvageneric.gif'
    return "/".join((base_url, icon,))


