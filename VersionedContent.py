# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $

# Zope
from OFS import Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime

# Silva
import SilvaPermissions
from Versioning import Versioning, VersioningError
from Content import Content

class VersionedContent(Content, Versioning, Folder.Folder):
    security = ClassSecurityInfo()
    
    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1

    _cached_datetime = None
    _cached_data = None
    
    # MANIPULATORS
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
    
    # ACCESSORS
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
                                        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_modification_datetime')
    def get_modification_datetime(self):
        """Get content modification date.
        """
        version_id = self.get_next_version() or self.get_public_version()
        if version_id is not None:
            return getattr(self, version_id).bobobase_modification_time()
        else:
            return self.bobobase_modification_time()
        
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

    security.declareProtected(SilvaPermissions.View, 'view')
    def view(self, view_type='public'):
        """
        """
        if view_type != 'public':
            return VersionedContent.inheritedAttribute('view')(self, view_type)

        if (self._cached_datetime is None or
                self._cached_datetime < self.get_public_version_publication_datetime() or
                self._cached_datetime < self.service_extensions.get_refresh_datetime()):
            data = VersionedContent.inheritedAttribute('view')(self, view_type)
            self._cached_datetime = DateTime()
            if self.is_cacheable():
                self._cached_data = data
            else:
                self._cached_data = None
        else:
            data = self._cached_data
            if data is None:
                data = VersionedContent.inheritedAttribute('view')(self, view_type)

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

    def manage_afterAdd(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_afterAdd')(self, item, container)
        for version in [self.get_unapproved_version(), self.get_approved_version(), self.get_public_version()] + self.get_previous_versions():
            if version:
                getattr(self, version).reindex_object()

    def manage_afterClone(self, item):
        CatalogedVersionedContent.inheritedAttribute('manage_afterClone')(self, item)
        for version in [self.get_unapproved_version(), self.get_approved_version(), self.get_public_version()] + self.get_previous_versions():
            if version:
                getattr(self, version).reindex_object()

    # Override this method from superclasses so we can remove all versions from the catalog
    def manage_beforeDelete(self, item, container):
        CatalogedVersionedContent.inheritedAttribute('manage_beforeDelete')(self, item, container)
        for version in [self.get_unapproved_version(), self.get_approved_version(), self.get_public_version()] + self.get_previous_versions():
            if version:
                getattr(self, version).unindex_object()

    def _reindex_version(self, version):
        if version[0] is None:
            return
        getattr(self, version[0]).reindex_object()
        
InitializeClass(CatalogedVersionedContent)

