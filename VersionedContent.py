# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.41 $

# Python
from StringIO import StringIO

# Zope
from OFS import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime

# Silva
import SilvaPermissions
from Versioning import Versioning
from Content import Content

from interfaces import IVersionedContent

class VersionedContent(Content, Versioning, Folder.Folder):
    security = ClassSecurityInfo()
    
    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1

    __implements__ = IVersionedContent

    def __init__(self, id):
        """Initialize VersionedContent.

        VersionedContent has no title of its own; its versions do.
        """
        VersionedContent.inheritedAttribute('__init__')(
            self, id, '[VersionedContent title bug]')
        self._cached_data = {}
    
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
        if self.id == 'index':
            container = self.get_container()
            container._invalidate_sidebar(container)
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'cleanPublicRenderingCache')
    def cleanPublicRenderingCache(self):
        """Cleans all current caching data from the cache.
        Currently this is only necessary for an upgrade of old content object
        which do not have cache yet.
        """
        self._cached_data = {}

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'create_copy')
    def create_copy(self):
        """Create new version of public version.
        """
        if self.get_next_version() is not None:
            return    
        # get id of public version to copy
        version_id_to_copy = self.get_public_version()
        # if there is no public version, get id of last closed version
        # (which should always be there)
        if version_id_to_copy is None:
            version_id_to_copy = self.get_last_closed_version()
            # there is no old version left!
            if version_id_to_copy is None:
                # FIXME: could create new empty version..
                raise  VersioningError, "Should never happen!"
        # copy published version
        new_version_id = str(self._version_count)
        self._version_count = self._version_count + 1
        # FIXME: this only works if versions are stored in a folder as
        # objects; factory function for VersionedContent objects should
        # create an initial version with name '0', too.
        # only testable in unit tests after severe hacking..
        self.manage_clone(getattr(self, version_id_to_copy),
                          new_version_id, self.REQUEST)
        self.create_version(new_version_id, None, None)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'revert_to_previous')
    def revert_to_previous(self):
        """Create a new version of public version, throw away the current one
        """
        # get the id of the version to revert to
        version_id_to_copy = (self.get_public_version() or
                              self.get_last_closed_version())
        if version_id_to_copy is None:
            raise VersioningError, "Should never happen!"
        # get the id of the current version
        current_version_id = self.get_unapproved_version()
        if current_version_id is None:
            raise VersioningError, "No unapproved version available"
        self._unindex_version((current_version_id,))
        # delete the current version
        self.manage_delObjects([current_version_id])
        # and copy the previous using the current id
        self.manage_clone(getattr(self, version_id_to_copy),
                          current_version_id, self.REQUEST)
        self._index_version((current_version_id,))


    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                             'get_title')
    def get_title(self):
        """Get title for public use, from published version.
        """
        viewable = self.get_viewable()
        if viewable is None:
            return "[No title available]"
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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        # Analogous to get_title
        viewable = self.get_viewable()
        if viewable is None:
            return "[No (short) title available]"
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_get_last_author_userid')
    def sec_get_last_author_userid(self):
        """Ask last userid of current transaction under edit.
        If it doesn't exist, get published version, or last closed.
        """
        version_id = (self.get_next_version() or
                      self.get_public_version() or
                      self.get_last_closed_version())
        # get the last transaction
        last_transaction = getattr(self,
                                   version_id).undoable_transactions(0, 1)
        if len(last_transaction) == 0:
            return None
        return last_transaction[0]['user_name']
                                        
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

    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self, view_type='public'):
        """
        """
        # XXX view_type=edit or add does not work anyway, but ...
        if view_type in ('edit','add'):
            return VersionedContent.inheritedAttribute('view')(self, view_type)

        data, cached_datetime = self._cached_data.get(view_type, (None, None))

        # this object is either not cached, or cache expired, or this
        # object is not published
        # XXX is_verson_published check triggers workflow update; necessary?
        if (cached_datetime is None or
             cached_datetime <= self.get_public_version_publication_datetime() or
             cached_datetime <= self.service_extensions.get_refresh_datetime() or
             not self.is_version_published()):

            # render the original way
            data = VersionedContent.inheritedAttribute('view')(self, view_type)
            if self.is_cacheable():
                # caching the data is allowed
                self._cached_data[view_type] = data, DateTime()
                self._cached_data = self._cached_data
            else:
                # remove from cache if caching is not allowed
                # only remove if there is something to remove,
                # avoiding creating a transaction each time
                if self._cached_data.has_key(view_type):
                    del self._cached_data[view_type]
                    self._cached_data = self._cached_data

        return data
        
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if the result of the view method can be safely
        cached.
        """
        # by default nothing is safely cacheable
        return 0

InitializeClass(VersionedContent)

class CatalogedVersionedContent(VersionedContent):
    """This class merely exists to mix VersionedContent with CatalogedVersioning
    """

    default_catalog = 'service_catalog'

    def manage_afterAdd(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_afterAdd')(self, item, container)
        for version in self._get_indexable_versions():
            # FIXME: what if e.g. version '0' got removed
            # but there is a content object with the id '0' in the
            # acquisition path? will this be indexed instead?
            version_object = getattr(self, version, None)
            if version_object is not None:
                version_object.reindex_object()

    def manage_afterClone(self, item):
        CatalogedVersionedContent.inheritedAttribute('manage_afterClone')(self, item)
        for version in self._get_indexable_versions():
            version_object = getattr(self, version, None)
            if version_object is not None:
                version_object.reindex_object()

    # Override this method from superclasses so we can remove all versions from the catalog
    def manage_beforeDelete(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_beforeDelete')(self, item, container)
        for version in self._get_indexable_versions():
            version_object = getattr(self, version, None)
            if version_object is not None:
                version_object.unindex_object()

    def _get_indexable_versions(self):
        ret = []
        for version in [self.get_unapproved_version(), 
                        self.get_approved_version(), 
                        self.get_public_version()
                        ] + self.get_previous_versions():
            if version:
                ret.append(version)
        return ret

    def _index_version(self, version):
        if version[0] is None:
            return None
        getattr(self, str(version[0])).index_object()
        
    def _reindex_version(self, version):
        if version[0] is None:
            return None
        getattr(self, str(version[0])).reindex_object()

    def _unindex_version(self, version):
        if version[0] is None:
            return None
        getattr(self, str(version[0])).unindex_object()
        
InitializeClass(CatalogedVersionedContent)

