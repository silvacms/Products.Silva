# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.80 $
# Zope
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass, DevelopmentMode
from DateTime import DateTime
# Silva
from Products.Silva import roleinfo
from Products.Silva import SilvaPermissions
from Products.Silva.Membership import noneMember
from Products.Silva.AccessManager import AccessManager

# Groups
try:
    # Are groups available?
    from Products.Groups.ZGroupsMapping import ZGroupsMapping
    from Products.Groups.GroupsErrors import GroupsError
    groups_enabled = 1
except ImportError:
    groups_enabled = 0

from interfaces import IContainer, IRoot

from Products.SilvaMetadata.Exceptions import BindingError

LOCK_DURATION = (1./24./60.)*20. # 20 minutes, expressed as fraction of a day

class Security(AccessManager):
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    security = ClassSecurityInfo()

    _last_author_userid = None
    _last_author_info = None
    _lock_info = None

    __ac_local_groups__ = None

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_assign')
    def sec_assign(self, userid, role):
        """Assign role to userid for this object.
        """
        if role not in roleinfo.ASSIGNABLE_ROLES:
            return
        # check whether we have permission to add Manager
        if (role == 'Manager' and
            not self.sec_have_management_rights()):
            return
        self.manage_addLocalRoles(userid, [role])

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_remove')
    def sec_remove(self, userid):
        """Remove a user completely from this object.
        """
        # FIXME: should this check for non Silva roles and keep
        # user if they exist?
        # can't remove managers if we don't have the rights to do so
        if ('Manager' in self.sec_get_roles_for_userid(userid) and
            not self.sec_have_management_rights()):
            return
        self.manage_delLocalRoles([userid])
    
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_revoke')
    def sec_revoke(self, userid, revoke_roles):
        """Remove roles from user in this object.
        """
        for role in revoke_roles:
            if role not in roleinfo.ASSIGNABLE_ROLES:
                return
            # can't revoke manager roles if we're not manager
            if (role == 'Manager' and
                not self.sec_have_management_rights()):
                return
        old_roles = self.get_local_roles_for_userid(userid)
        roles = [role for role in old_roles if role not in revoke_roles]
        if len(roles) > 0:
            self.manage_setLocalRoles(userid, roles)
        else:
            # if no more roles, remove user completely
            self.sec_remove(userid)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_create_lock')
    def sec_create_lock(self):
        """Create lock for this object. Return true if successful.
        """
        if self.sec_is_locked():
            return 0
        user_id = getSecurityManager().getUser().getId()
        dt = DateTime()
        self._lock_info = user_id, dt
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_break_lock')
    def sec_break_lock(self):
        """Breaks the lock.
        """
        self._lock_info = None

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_is_locked')
    def sec_is_locked(self):
        """Check whether this object is locked by a user currently
        editing.
        """
        if self._lock_info is None:
            return 0
        user_id, dt = self._lock_info
        current_dt = DateTime()
        if current_dt - dt >= LOCK_DURATION:
            return 0
        current_user_id = getSecurityManager().getUser().getId()
        return user_id != current_user_id

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_have_management_rights')
    def sec_have_management_rights(self):
        """Check whether we have management rights here.
        """
        return getSecurityManager().getUser().has_role(['Manager'], self)

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_userids')
    def sec_get_userids(self):
        """Get the userids that have local roles here that we care about.
        """
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in roleinfo.ASSIGNABLE_ROLES:
                    result.append(userid)
                    break
        return result

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_userids_deep')
    def sec_get_userids_deep(self):
        """Get all userids that have local roles in anything under this
        object.
        """
        l = []
        self._sec_get_userids_deep_helper(l)
        # now make sure we have only one of each userid
        dict = {}
        for userid in l:
            dict[userid] = 0
        return dict.keys()

    def _sec_get_userids_deep_helper(self, l):
        for userid in self.sec_get_userids():
            l.append(userid)
        if IContainer.providedBy(self):
            for item in self.get_ordered_publishables():
                item._sec_get_userids_deep_helper(l)
            for item in self.get_nonactive_publishables():
                item._sec_get_userids_deep_helper(l)
            for item in self.get_assets():
                item._sec_get_userids_deep_helper(l)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_nearest_of_role')
    def sec_get_nearest_of_role(self, role):
        """Get a list of userids that have a role in this context. This
        goes up the tree and finds the nearest user(s) that can be found.
        """
        obj = self.aq_inner
        while 1:
            # get all users defined on this object
            userids = obj.sec_get_userids()
            if userids:
                result = []
                for userid in userids:
                    if (role in obj.sec_get_roles_for_userid(userid) and 
                            self.service_members.get_member(userid)):
                        result.append(userid)
                if result:
                    return result
                
            if IRoot.providedBy(obj):
                break
            obj = obj.aq_parent
        return []
    
    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_roles_for_userid')
    def sec_get_roles_for_userid(self, userid):
        """Get the local roles that a userid has here.
        """
        return [role for role in self.get_local_roles_for_userid(userid)
                if role in roleinfo.ASSIGNABLE_ROLES]
    
    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'sec_get_roles')
    def sec_get_roles(self):
        """Get all roles defined here that we can manage, given the
        roles of this user.
        """
        return roleinfo.ASSIGNABLE_ROLES

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_find_users')
    def sec_find_users(self, search_string):
        """Find users in user database. This method delegates to
        service_members for security reasons.
        """
        # XXX this loop seems useless, why is it here? (maybe we need a copy?)
        members = []
        for member in self.service_members.find_members(search_string):
            members.append(member)
        return members

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_member')  
    def sec_get_member(self, userid):
        """Get information for userid. This method delegates to
        service_members for security reasons.
        """
        return self.service_members.get_cached_member(userid)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'sec_get_last_author_info')
    def sec_get_last_author_info(self):
        """Get the info of the last author (this is a IMember object)
        """
        # containers have no author
        if IContainer.providedBy(self):
            return noneMember.__of__(self)
        
        # get cached author info (may be None)
        version = self.get_previewable()
        if version is None:
            return noneMember.__of__(self)
        
        info = getattr(version, '_last_author_info', None)
        if info is None:
            return noneMember.__of__(self)
        else:
            return info.__of__(self)
            
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_update_last_author_info')
    def sec_update_last_author_info(self):
        """Update the author info with the current author.
        """
        version = self.get_editable()
        if version is not None:
            userid = getSecurityManager().getUser().getId()
            version._last_author_userid = userid
            version._last_author_info = self.sec_get_member(userid).aq_base
            # XXX performance issue?
            try:
                binding = self.service_metadata.getMetadata(version)
            except BindingError:
                return
            if binding is None:
                return
            now = DateTime()
            binding.setValues('silva-extra', {'modificationtime': now})        

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_get_creator_info')
    def sec_get_creator_info(self):
        return self.sec_get_member(self.getOwner().getId())

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_local_defined_userids')
    def sec_get_local_defined_userids(self):
        """Get the list of userids with locally defined roles
        """
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in roleinfo.ASSIGNABLE_ROLES:
                    result.append(userid)
                    break
        return result

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'sec_get_local_roles_for_userid')
    def sec_get_local_roles_for_userid(self, userid):
        """Get a list of local roles that a userid has here
        """
        return [role for role in self.get_local_roles_for_userid(userid)
                if role in roleinfo.ASSIGNABLE_ROLES]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_get_all_roles')
    def sec_get_all_roles(self):
        """Returns all roles the currently logged in user has in this
        context"""
        roles = []
        for role in roleinfo.ASSIGNABLE_ROLES[:]:
            if self.REQUEST.AUTHENTICATED_USER.has_role(role, self):
                roles.append(role)
        return roles

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_defined_userids')
    def sec_get_upward_defined_userids(self):
        """Get the list of userids with roles defined in a higer
        level of the tree
        """
        userids = {}
        parent = self.aq_inner.aq_parent
        while IContainer.providedBy(parent):
            for userid in parent.sec_get_local_defined_userids():
                userids[userid] = 1
            parent = parent.aq_inner.aq_parent
        return userids.keys()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_roles_for_userid')
    def sec_get_upward_roles_for_userid(self, userid):
        """Get the roles that a userid has here, defined in a higer
        level of the tree
        """
        roles = {}
        parent = self.aq_inner.aq_parent
        while IContainer.providedBy(parent):
            for role in parent.sec_get_local_roles_for_userid(userid):
                roles[role] = 1
            parent = parent.aq_inner.aq_parent
        return roles.keys()
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_downward_defined_userids')
    def sec_get_downward_defined_userids(self):
        """Get the list of userids with roles defined in a lower
        level of the tree (these users do not have rights on this
        local level)
        """
        d = {}
        self._sec_get_downward_defined_userids_helper(d)
        return d.keys()

    def _sec_get_downward_defined_userids_helper(self, d):
        for userid in self.sec_get_userids():
            d[userid] = 1
        if IContainer.providedBy(self):
            for item in self.get_ordered_publishables():
                item._sec_get_downward_defined_userids_helper(d)
            for item in self.get_nonactive_publishables():
                item._sec_get_downward_defined_userids_helper(d)
            for item in self.get_assets():
                item._sec_get_downward_defined_userids_helper(d)

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_clean_roles')
    def sec_clean_roles(self):
        """Clean all roles where the corresponding user is no longer available
        """
        # this is possibly horribly inefficient, but the simplest way
        # to implement this.
        valid_user_ids = self.get_valid_userids()
        invalid_user_ids = [ user_id for user_id in self.sec_get_local_defined_userids()
                             if user_id not in valid_user_ids ]
        self.manage_delLocalRoles(invalid_user_ids)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_members_for_userids')
    def sec_get_members_for_userids(self, userids):
        d = {}
        
        for userid in userids:
            d[userid] = self.sec_get_member(userid)
        return d

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_groups_enabled')
    def sec_groups_enabled(self):
        """Are groups enabled in this Silva site
        """
        return groups_enabled

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_local_defined_groups')
    def sec_get_local_defined_groups(self):
        """Get the list of groups with locally defined roles.
        """
        local_groups = self.__ac_local_groups__
        if local_groups is None:
            return []
        return local_groups.getMappings().keys()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_local_roles_for_group')
    def sec_get_local_roles_for_group(self, group):
        """Get a list of local roles that are defined for a group here.
        """
        local_groups = self.__ac_local_groups__
        if local_groups is None:
            return []
        return local_groups.getMappings().get(group, [])

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_defined_groups')
    def sec_get_upward_defined_groups(self):
        """Get the list of groups with roles defined in a higer
        level of the tree.
        """
        parent = self.aq_inner.aq_parent
        groups = {}
        while IContainer.providedBy(parent):
            for group in parent.sec_get_local_defined_groups():
                groups[group] = 1
            parent = parent.aq_inner.aq_parent
        return groups.keys()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_roles_for_group')
    def sec_get_upward_roles_for_group(self, group):
        """Get the roles that a group has here, defined in a higer
        level of the tree.
        """
        parent = self.aq_inner.aq_parent
        roles = {}
        while IContainer.providedBy(parent):
            for role in parent.sec_get_local_roles_for_group(group):
                roles[role] = 1
            parent = parent.aq_inner.aq_parent
        return roles.keys()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_downward_defined_groups')
    def sec_get_downward_defined_groups(self):
        """Get the list of groups with roles defined in a lower
        level of the tree.
        """
        d = {}
        self._sec_get_downward_defined_groups_helper(d)
        return d.keys()
    
    def _sec_get_downward_defined_groups_helper(self, d):
        for group in self.sec_get_local_defined_groups():
            d[group] = 1
        if IContainer.providedBy(self):
            for item in self.get_ordered_publishables():
                item._sec_get_downward_defined_groups_helper(d)
            for item in self.get_nonactive_publishables():
                item._sec_get_downward_defined_groups_helper(d)
            for item in self.get_assets():
                item._sec_get_downward_defined_groups_helper(d)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_groupsmapping')
    def sec_get_groupsmapping(self):
        """Return the groupmappings for this object.
        """
        return self.__ac_local_groups__
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_or_create_groupsmapping')
    def sec_get_or_create_groupsmapping(self):
        """Return the groupmappings for this object. Create one of currently
        no mapping exists.
        """
        if not groups_enabled:
            return None

        if not self.__ac_local_groups__:
            self.__ac_local_groups__ = ZGroupsMapping('acl_groups')
        return self.sec_get_groupsmapping()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_cleanup_groupsmapping')
    def sec_cleanup_groupsmapping(self):
        """If called, check to see whether any mappings are defined in the
        mappings object. If not, clear the __ac_local_groups__ attribute
        for efficiency.
        """
        if self.__ac_local_groups__:
            if not self.__ac_local_groups__.getMappings():
                self.__ac_local_groups__ = None

    # XXX where does this method belong? it needs to be accessible
    # from page templates easily so i put it here
    security.declarePublic('sec_in_development_mode')
    def sec_in_development_mode(self):
        """Returns true if the site is in development mode and user is
        Manager.
        """
        is_manager = getSecurityManager().getUser().has_role(
            ['Manager'], object=self)
        return DevelopmentMode and is_manager
    
InitializeClass(Security)
