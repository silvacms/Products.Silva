import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from Products.Silva.adapters import adapter
from Products.Silva.adapters.interfaces import IVersionManagement
from Products.Silva.interfaces import IVersion
from Products.Silva.Versioning import VersioningError
from Products.Silva import SilvaPermissions
from Products.Silva.Membership import noneMember

from Products.Silva.i18n import translate as _

module_security = ModuleSecurityInfo('Products.Silva.adapters.version_management')

class VersionManagementAdapter(adapter.Adapter):
    """Adapter to manage Silva versions (duh?)"""
    
    __implements__ = IVersionManagement
    security = ClassSecurityInfo()

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionById')
    def getVersionById(self, id):
        return getattr(self.context, id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getPublishedVersion')
    def getPublishedVersion(self):
        id = self.context.get_public_version()
        if id is not None:
            return getattr(self.context, id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getUnapprovedVersion')
    def getUnapprovedVersion(self):
        id = self.context.get_unapproved_version()
        if id is not None:
            return getattr(self.context, id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getApprovedVersion')
    def getApprovedVersion(self):
        id = self.context.get_approved_version()
        if id is not None:
            return getattr(self.context, id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionIds')
    def getVersionIds(self):
        objects = self.context.objectValues()
        ret = []
        for object in objects:
            if IVersion.isImplementedBy(object):
                ret.append(object.id)
        return ret

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersions')
    def getVersions(self, sort_attribute='id'):
        objects = [o for o in self.context.objectValues() if 
                    IVersion.isImplementedBy(o)]
        if sort_attribute == 'id':
            objects.sort(lambda a, b: cmp(int(a.id), int(b.id)))
        elif sort_attribute:
            objects.sort(
                lambda a, b: 
                    cmp(
                        getattr(a, sort_attribute), 
                        getattr(b, sort_attribute)
                    )
                )
        return objects

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'revertPreviousToEditable')
    def revertPreviousToEditable(self, copy_id):
        if not hasattr(self.context, copy_id):
            raise AttributeError, copy_id

        approved_version = self.getApprovedVersion()
        if approved_version is not None:
            raise VersioningError, _('No unapproved version available')
            
        current_version = self.getUnapprovedVersion()
        # move the current editable version to _previous_versions
        if current_version is not None:
            current_version_id = current_version.id
            status = self.getVersionStatus(current_version_id)
            if status in ('pending', 'approved'):
                raise VersioningError, _('No unapproved version available')
            
            version_tuple = self.context._unapproved_version 
            if self.context._previous_versions is None:
                self.context._previous_versions = []
            self.context._previous_versions.append(version_tuple)
            self.context._unindex_version(current_version_id)
        # just hope for the best... scary API
        new_version_id = self._createUniqueId()
        self.context.manage_clone(getattr(self.context, copy_id), new_version_id)
        self.context._unapproved_version = (new_version_id, None, None)
        self.context._index_version(new_version_id)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'deleteVersions')
    def deleteVersions(self, ids):
        """Delete a number of versions
        
            If all versions are selected, a VersioningError is raised, apart
            from that this will try to delete as much as possible and return
            a list of tuples (id, errorstring) (where errorstring is None for
            a successful deletion).
        """
        if len(ids) == len(self.getVersionIds()):
            raise VersioningError, _('Can not delete all versions')
        ret = []
        delids = []
        for id in ids:
            approved = self.getApprovedVersion()
            if approved is not None and approved.id == id:
                ret.append((id, 'version is approved'))
                continue
            published = self.getPublishedVersion()
            if published is not None and published.id == id:
                ret.append((id, 'version is published'))
                continue
            # remove any reference from the version list
            # we can skip approved and published, since we checked those above
            unapproved = self.getUnapprovedVersion()
            if unapproved is not None and unapproved.id == id:
                self.context._unapproved_version = (None, None, None)
                self.context._p_changed = 1
            else:
                # XXX it's a pity we have to traverse the whole list for each
                # id...
                for version in self.context._previous_versions:
                    if version[0] == id:
                        self.context._previous_versions.remove(version)
            delids.append(id)
            ret.append((id, None))
        delret = self.context.manage_delObjects(delids)
        return ret

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                                'deleteOldVersions')
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionModificationTime')
    def getVersionModificationTime(self, versionid):
        version = getattr(self.context, versionid)
        binding = self.context.service_metadata.getMetadata(version)
        if binding is None:
            return None
        return binding['silva-extra']['modificationtime']

    # XXX currently the following 2 methods have a very non-optimal 
    # implementation, hopefully in the future we can change the underlying
    # Versioning and VersionedContent layers and store these times on the
    # version objects rather then on the VersionedContent
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionPublicationTime')
    def getVersionPublicationTime(self, versionid):
        if (self.context._unapproved_version[0] is not None and 
                self.context._unapproved_version[0] == versionid):
            return self.context._unapproved_version[1]
        elif (self.context._approved_version[0] is not None and
                self.context._approved_version[0] == versionid):
            return self.context._approved_version[1]
        elif (self.context._public_version[0] is not None and 
                self.context._public_version[0] == versionid):
            return self.context._public_version[1]
        else:
            if self.context._previous_versions:
                for verid, pubtime, exptime in self.context._previous_versions:
                    if verid == versionid:
                        return pubtime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionExpirationTime')
    def getVersionExpirationTime(self, versionid):
        if (self.context._unapproved_version[0] is not None and 
                self.context._unapproved_version[0] == versionid):
            return self.context._unapproved_version[2]
        elif (self.context._approved_version[0] is not None and
                self.context._approved_version[0] == versionid):
            return self.context._approved_version[2]
        elif (self.context._public_version[0] is not None and 
                self.context._public_version[0] == versionid):
            return self.context._public_version[2]
        else:
            if self.context._previous_versions:
                for verid, pubtime, exptime in self.context._previous_versions:
                    if verid == versionid:
                        return exptime

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionLastAuthorInfo')
    def getVersionLastAuthorInfo(self, versionid):
        version = self.getVersionById(versionid)
        info = getattr(version, '_last_author_info', None)
        if info is None:
            return noneMember.__of__(self.context)
        else:
            return info.__of__(self.context)
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionCreatorInfo')
    def getVersionCreatorInfo(self, versionid):
        version = self.getVersionById(versionid)
        return self.context.sec_get_member(version.getOwner().getUserName())

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                'getVersionStatus')
    def getVersionStatus(self, versionid):
        """Returns the status of a version as a string

            return value can be one of the following strings:

                unapproved
                pending
                approved
                published
                last_closed
                closed
        """
        if (self.context._unapproved_version[0] is not None and 
                self.context._unapproved_version[0] == versionid):
            if self.context.is_version_approval_requested():
                return 'pending'
            else:
                return 'unapproved'
        elif (self.context._approved_version[0] is not None and
                self.context._approved_version[0] == versionid):
            return 'approved'
        elif (self.context._public_version[0] is not None and 
                self.context._public_version[0] == versionid):
            return 'published'
        else:
            if self.context._previous_versions:
                if self.context._previous_versions[-1][0] == versionid:
                    return 'last_closed'
                else:
                  for (vid, vpt, vet) in self.context._previous_versions:
                    if vid == versionid:
                      return 'closed'
        msg = _('no such version ${version}')
        msg.set_mapping({'version': versionid})
        raise VersioningError, msg

    def _createUniqueId(self):
        # for now we use self.context._version_count, we may
        # want to get rid of that nasty trick in the future though...
        newid = str(self.context._version_count)
        self.context._version_count += 1
        return newid
    
Globals.InitializeClass(VersionManagementAdapter)

def __allow_access_to_unprotected_subobjects__(name, value=None):
    return name in ('getVersionManagementAdapter')

module_security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                  'getVersionManagementAdapter')
def getVersionManagementAdapter(context):
    return VersionManagementAdapter(context).__of__(context)
    
