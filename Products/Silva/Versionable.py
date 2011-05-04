# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok

# Zope 2
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import InitializeClass
from zExceptions import NotFound

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.Versioning import Versioning

from silva.core.interfaces import IVersionable
from silva.core.services.catalog import Cataloging
from silva.core.services.interfaces import ICataloging, ICatalogingAttributes
from silva.core.services.catalog import Cataloging

class Versionable(Versioning):
    """An in-between for Versioning to support SilvaObject which are versioned.
       This class overrides SilvaObject api for versioned objects, which can be
       either content (IVersionedContent) or asset (IVersionedAsset)"""
    
    grok.baseclass()
    grok.implements(IVersionable)
    
    security = ClassSecurityInfo()
    
    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1

    # MANIPULATORS
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set title of version under edit.
        """
        editable = self.get_editable()
        if editable is None:
            return
        editable.set_title(title)
    
    # ACCESSORS
    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')    
    def can_set_title(self):
        """Check to see if the title can be set
        """
        return bool(self.get_editable())

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'get_title')
    def get_title(self):
        """Get title for public use, from published version.
        """
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_editable')
    def get_title_editable(self):
        """Get title for editable or previewable use
        """
        # Ask for 'previewable', which will return either the 'next version'
        # (which may be under edit, or is approved), or the public version, 
        # or, as a last resort, the closed version.
        # This to be able to show at least some title in the Silva edit
        # screens.
        previewable = self.get_previewable()
        if previewable is None:
            return "[No title available]"
        return previewable.get_title()
 
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title_or_id_editable')
    def get_title_or_id_editable(self):
        """Get title or id editable or previewable use.
        """
        title = self.get_title_editable()
        if title.strip() == '':
            return self.id
        else:
            return title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        # Analogous to get_title
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_short_title()


    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get short_title for editable or previewable use
        """
        # Analogous to get_title_editable
        previewable = self.get_previewable()
        if previewable is None:
            return "[No (short) title available]"
        return previewable.get_short_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_nav_title')
    def get_nav_title(self):
        """Get nav_title for public use, from published version.
        """
        # Analogous to get_title
        viewable = self.get_viewable()
        if viewable is None:
            return self.id
        return viewable.get_nav_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_nav_title_editable')
    def get_nav_title_editable(self):
        """Get nav_title for editable or previewable use
        """
        # Analogous to get_title_editable
        previewable = self.get_previewable()
        if previewable is None:
            return "[No (nav) title available]"
        return previewable.get_nav_title()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_editable')
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        # the editable version is the unapproved version
        version_id = self.get_unapproved_version()
        if version_id is None:
            return None # there is no editable version
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_previewable')
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_public_version()
            if version_id is None:
                version_id = self.get_last_closed_version()
                if version_id is None:
                    return None
        return getattr(self, version_id)


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_viewable')
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        version_id = self.get_public_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_last_closed')
    def get_last_closed(self):
        """Get the last closed version (may be the object itself if
        no versioning).
        """
        version_id = self.get_last_closed_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
        'is_deletable')
    def is_deletable(self):
        """is object deletable?
        
            a publishable object is only deletable if
                it's not published
                it's not approved
        
        """
        return not self.is_published() and not self.is_approved()
InitializeClass(Versionable)

class VersionableCataloging(Cataloging):
    """Cataloging support for versionable content
    """
    grok.context(IVersionable)

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
        super(VersionableCataloging, self).index(indexes=indexes)
        for version in self.get_indexable_versions():
            attributes = ICatalogingAttributes(version)
            path = '/'.join((self._path, version.getId(),))
            self._catalog.catalog_object(attributes, path)

    def unindex(self):
        if self._catalog is None:
            return
        super(VersionableCataloging, self).unindex()
        for version in self.get_indexable_versions():
            path = '/'.join((self._path, version.getId(),))
            self._catalog.uncatalog_object(path)