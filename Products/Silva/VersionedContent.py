# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import InitializeClass
from OFS.Folder import Folder as BaseFolder
from zExceptions import NotFound

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Versionable import Versionable
from Products.Silva.Content import Content

from silva.core.interfaces import IVersionedContent, ICatalogedVersionedContent
from silva.core.services.catalog import Cataloging
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes


class VersionedContent(Versionable, Content, BaseFolder):
    security = ClassSecurityInfo()

    grok.implements(IVersionedContent)
    grok.baseclass()

    # Set ZMI tabs
    manage_options = (
        (BaseFolder.manage_options[0], ) +
        ({'label': 'Silva /edit...', 'action':'edit'},)+
        BaseFolder.manage_options[1:])

    # MANIPULATORS

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set title of version under edit.  
           Overriden to also invalidate sidebar when object is index
        """
        super(VersionedContent, self).set_title(title)
        if self.id == 'index':
            container = self.get_container()
            container._invalidate_sidebar(container)

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'view_version')
    def view_version(self, version=None):
        version_name = self.REQUEST.other.get('SILVA_PREVIEW_NAME', '')
        if version_name:
            version = getattr(self, version_name, None)
            if version is None:
                raise NotFound(version_name)
        return super(VersionedContent, self).view_version(version)

    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if the result of the view method can be safely
        cached.
        """
        # by default nothing is safely cacheable
        return 0

InitializeClass(VersionedContent)

class CatalogedVersionedContent(VersionedContent):
    """VersionedContent from those versions are in the catalog.
    """
    grok.implements(ICatalogedVersionedContent)
    grok.baseclass()

    def _index_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).index()

    def _reindex_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).reindex()

    def _unindex_version(self, version_id):
        version = getattr(self, version_id, None)
        if version is not None:
            # XXX Update this
            ICataloging(version).unindex()

InitializeClass(CatalogedVersionedContent)


class VersionedContentCataloging(Cataloging):
    """Cataloging support for versioned content.
    """
    grok.context(ICatalogedVersionedContent)

    def get_indexable_versions(self):
        version_ids = [
            self.context.get_next_version(),
            self.context.get_public_version(),]
        for version_id in version_ids:
            if version_id is None:
                continue
            if hasattr(aq_base(self.context), version_id):
                yield getattr(self.context, version_id)

    def index(self, indexes=None):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).index(indexes=indexes)
        for version in self.get_indexable_versions():
            attributes = ICatalogingAttributes(version)
            path = '/'.join((self._path, version.getId(),))
            self._catalog.catalog_object(attributes, path)

    def unindex(self):
        if self._catalog is None:
            return
        super(VersionedContentCataloging, self).unindex()
        for version in self.get_indexable_versions():
            path = '/'.join((self._path, version.getId(),))
            self._catalog.uncatalog_object(path)
