from Content import Content
from Versioning import Versioning, VersioningError

class VersionedContent(Content, Versioning):
    # there is always at least a single version to start with,
    # created by the object's factory function
    _version_count = 1
    
    # MANIPULATORS
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
    def get_editable(self):
        """Get the editable version (may be object itself if no versioning).
        """
        # the editable version is the unapproved version
        version_id = self.get_unapproved_version()
        if version_id is None:
            return None # there is no editable version
        return getattr(self, version_id)
        
    def get_previewable(self):
        """Get the previewable version (may be the object itself if no
        versioning).
        """
        version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_public_version()
            if version_id is None:
                return None
        return getattr(self, version_id)
    
    def get_viewable(self):
        """Get the publically viewable version (may be the object itself if
        no versioning).
        """
        version_id = self.get_public_version()
        if version_id is None:
            return None # There is no public document
        return getattr(self, version_id)
        
