import Globals
from Products.Silva.adapters import adapter
from Products.Silva.adapters.interfaces import IVersionManagement
from Products.Silva.Versioning import VersioningError

class VersionManagementAdapter(adapter.Adapter):
    """Adapter to manage Silva versions (duh?)"""
    
    __implements__ = IVersionManagement

    def getVersionById(self, id):
        return getattr(self.context, id)

    def getPublishedVersion(self):
        id = self.context.get_public_version()
        if id is not None:
            return getattr(self.context, id)

    def getUnapprovedVersion(self):
        id = self.context.get_unapproved_version()
        if id is not None:
            return getattr(self.context, id)

    def getApprovedVersion(self):
        id = self.context.get_approved_version()
        if id is not None:
            return getattr(self.context, id)

    def getVersionIds(self):
        return self.context.objectIds('Silva Document Version')

    def revertEditableToOld(self, copy_id):
        if not hasattr(self.context, copy_id):
            raise AttributeError, copy_id
        current_version = self.getUnapprovedVersion()
        # move the current editable version to _previous_versions
        if current_version is not None:
            # throw away publication and expiration time, they can only get 
            # in the way later
            current_version_id = current_version.id
            version_tuple = (current_version_id, None, None)
            self.context._previous_versions.append(version_tuple)
            self._reindex_version(current_version_id)
        # just hope for the best... scary API
        new_version_id = self._createUniqueId()
        self.context.manage_clone(getattr(self.context, copy_id), new_version_id)
        # rather then replacing the current editable version (as 
        # Versioning.revert_to_previous() does) we create a new one
        self.context.create_version(new_version_id, None, None)

    def getVersions(self, sort_attribute='id'):
        ids = self.context.objectValues('Silva Document Version')
        if sort_attribute == 'id':
            ids.sort(lambda a, b: cmp(int(a.id), int(b.id)))
        elif sort_attribute:
            ids.sort(
                lambda a, b: 
                    cmp(
                        getattr(a, sort_attribute), 
                        getattr(b, sort_attribute)
                    )
                )
        return ids

    def deleteVersion(self, id):
        if not id in self.context.objectIds('Silva Document Version'):
            raise AttributeError, id
        self.context.manage_delObjects([id])

    def deleteOldVersions(self, number_to_keep=0):
        versions = self.getVersionIds()
        unapproved = self.getUnapprovedVersion()
        approved = self.getApprovedVersion()
        public = self.getPublishedVersion()
        if unapproved is not None and unapproved.id in versions:
            versions.remove(unapproved.id)
        if approved is not None and unapproved.id in versions:
            versions.remove(approved.id)
        if public is not None and public.id in versions:
            versions.remove(public.id)
        if len(versions) > number_to_keep:
            if number_to_keep > 0:
                versions = versions[:-number_to_keep]
            self.context.manage_delObjects(versions)

    def _createUniqueId(self):
        ids = self.getVersionIds()
        testid = int(ids[-1]) + 1
        while str(testid) in ids:
            testid += 1
        return str(testid)
    
Globals.InitializeClass(VersionManagementAdapter)

def getVersionManagementAdapter(context):
    return VersionManagementAdapter(context).__of__(context)
    
