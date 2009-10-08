# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

"""Silva icon registry"""

from five import grok

# Silva
from silva.core.interfaces import IFile, ISilvaObject, \
    IGhostContent, IGhostFolder


class SilvaIcons(grok.DirectoryResource):
    # This export the globals directory using Zope 3 technology.
    grok.path('icons')
    grok.name('silva.icons')


class IconRegistry(object):

    def __init__(self):
        self._icon_mapping = {}

    def getIcon(self, object):
        if IGhostContent.providedBy(object):
            version = object.getLastVersion()
            if version.get_link_status() == version.LINK_OK:
                kind = 'link_ok'
            else:
                kind = 'link_broken'
            identifier = ('ghost', kind)
        elif IGhostFolder.providedBy(object):
            if object.get_link_status() == object.LINK_OK:
                if object.implements_publication():
                    kind = 'publication'
                else:
                    kind = 'folder'
            else:
                kind = 'link_broken'
            identifier = ('ghostfolder', kind)
        elif IFile.providedBy(object):
            identifier = ('mime_type', object.get_mime_type())
        elif ISilvaObject.providedBy(object):
            identifier = ('meta_type', object.meta_type)
        else:
            meta_type = getattr(object, 'meta_type', None)
            if meta_type is None:
                raise ValueError, "Icon not found"
            identifier = ('meta_type', meta_type)
        return self.getIconByIdentifier(identifier)

    def getIconByIdentifier(self, identifier):
        icon = self._icon_mapping.get(identifier, None)
        if icon is None:
            msg = "No icon for %s" % repr(identifier)
            raise RegistryError, msg
        return icon

    def registerIcon(self, identifier, icon_name):
        """Register an icon.

        NOTE: this will overwrite previous icon declarations
        """
        url_path = '++resources++silva.icons/%s' % icon_name
        self._icon_mapping[identifier] = icon_name


registry = IconRegistry()

