# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.30 $
# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime
# Silva interfaces
from IContainer import IContainer
# Silva
import SilvaPermissions
from UserManagement import user_management

# Are groups available?
try:
    from Products.Groups.ZGroupsMapping import ZGroupsMapping
    groups_enabled = 1
except ImportError:
    groups_enabled = 0

LOCK_DURATION = 1./24./3./20. # 20 minutes, um 1 minute

interesting_roles = ['Reader', 'Author', 'Editor', 'ChiefEditor', 'Manager']

class Security:
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
        if role not in interesting_roles:
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
            if role not in interesting_roles:
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

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_open_to_public')
    def sec_open_to_public(self):
        """Open this object to the public; accessible to everybody (if
        at least container is accessible).
        """
        #self.manage_permission('Access contents information',
        #                       roles=[],
        #                       acquire=1)
        self.manage_permission('View',
                               roles=[],
                               acquire=1)

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_close_to_public')
    def sec_close_to_public(self):
        """Close this object to the public; only accessible to people
        with Viewer role here.
        """
        # XXX should change this on dependencies on permissions somehow, not
        # hard coded roles
        allowed_roles = ['Viewer', 'Reader', 'Author', 'Editor', 
                         'ChiefEditor', 'Manager']
        #self.manage_permission('Access contents information',
        #                       roles=allowed_roles,
        #                       acquire=0)
        self.manage_permission('View',
                               roles=allowed_roles,
                               acquire=0)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_create_lock')
    def sec_create_lock(self):
        """Create lock for this object. Return true if successful.
        """
        if self.sec_is_locked():
            return 0
        username = self.REQUEST.AUTHENTICATED_USER.getUserName()
        dt = DateTime()
        self._lock_info = username, dt
        return 1
    
    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_is_open_to_public')
    def sec_is_open_to_public(self):
        """Check whether this is opened.
        """
        # XXX ugh
        for role_info in self.rolesOfPermission('View'):
            if (role_info['name'] == 'Viewer' and
                role_info['selected'] == 'SELECTED'):
                return 0
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_is_locked')
    def sec_is_locked(self):
        """Check whether this object is locked by a user currently
        editing.
        """
        if self._lock_info is None:
            return 0
        username, dt = self._lock_info
        current_dt = DateTime()
        if current_dt - dt >= LOCK_DURATION:
            return 0
        current_username = self.REQUEST.AUTHENTICATED_USER.getUserName()
        return username != current_username
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_have_management_rights')
    def sec_have_management_rights(self):
        """Check whether we have management rights here.
        """
        return self.REQUEST.AUTHENTICATED_USER.has_role(['Manager'], self)
    
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_user_ids')
    def sec_get_userids(self):
        """Get the userids that have local roles here that we care about.
        """
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in interesting_roles:
                    result.append(userid)
                    break
        return result

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_userids_deep')
    #DEPRECATED
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

    #DEPRECATED
    def _sec_get_userids_deep_helper(self, l):
        for userid in self.sec_get_userids():
            l.append(userid)
        if IContainer.isImplementedBy(self):
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
                    if role in obj.sec_get_roles_for_userid(userid):
                        result.append(userid)
                if result:
                    return result
                
            # XXX: this is depending on meta type, but should be unique..
            if obj.meta_type == 'Silva Root':
                break
            obj = obj.aq_parent
        return []
    
    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_get_roles_for_userid')
    def sec_get_roles_for_userid(self, userid):
        """Get the local roles that a userid has here.
        DEPRECATED
        """
        return [role for role in self.get_local_roles_for_userid(userid)
                if role in interesting_roles]
    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_roles')
    #DEPRECATED
    def sec_get_roles(self):
        """Get all roles defined here that we can manage, given the
        roles of this user.
        """
        return interesting_roles

    security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
                              'sec_find_users')
    def sec_find_users(self, userid):
        """Find users in user database.
        """
        return user_management.find_users(self, userid)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_user_info')  
    def sec_get_user_info(self, userid):
        """Get information for userid. FIXME: describe which info fields
        exist.
        """
        return user_management.get_user_info(self, userid)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'sec_get_last_author_info')
    def sec_get_last_author_info(self):
        """Get the info of the last author (provide at least cn and
        userid).
        """
        # containers have no author
        if IContainer.isImplementedBy(self):
            return { 'cn': '', 'userid': None }

        # unknown author if none assigned yet
        if not self._last_author_userid:
            return { 'cn': 'Unknown author', 'userid': None }
        # authorwise get cached author info
        return self._last_author_info

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'sec_set_last_author_info')
    def sec_update_last_author_info(self):
        """Update the author info with the current author.
        """
        self._last_author_userid = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._last_author_info = self.sec_get_user_info(self._last_author_userid)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_local_defined_userids')
    def sec_get_local_defined_userids(self):
        """Get the list of userids with locally defined roles
        """
        result = []
        for userid, roles in self.get_local_roles():
            for role in roles:
                if role in interesting_roles:
                    result.append(userid)
                    break
        return result

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_local_roles_for_userid')
    def sec_get_local_roles_for_userid(self, userid):
        """Get a list of local roles that a userid has here
        """
        return [role for role in self.get_local_roles_for_userid(userid)
                if role in interesting_roles]

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_defined_userids')
    def sec_get_upward_defined_userids(self):
        """Get the list of userids with roles defined in a higer
        level of the tree
        """
        userids = {}
        parent = self.aq_inner.aq_parent
        while IContainer.isImplementedBy(parent):
            for userid in parent.sec_get_local_defined_userids():
                userids[userid] = 1
            parent = parent.aq_parent
        return userids.keys()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_roles_for_userid')
    def sec_get_upward_roles_for_userid(self, userid):
        """Get the roles that a userid has here, defined in a higer
        level of the tree
        """
        roles = {}
        parent = self.aq_inner.aq_parent
        while IContainer.isImplementedBy(parent):
            for role in parent.sec_get_local_roles_for_userid(userid):
                roles[role] = 1
            parent = parent.aq_parent
        return roles.keys()
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_downward_defined_userids')
    def sec_get_downward_defined_userids(self):
        """Get the list of userids with roles defined in a lower
        level of the tree (these users do not have rights on this
        local level)
        """
        d = {}
        self._sec_get_userids_deep_helper(d)
        return d.keys()

    def _sec_get_downward_defined_userids_helper(self, d):
        for userid in self.sec_get_userids():
            d[userid] = 1
        if IContainer.isImplementedBy(self):
            for item in self.get_ordered_publishables():
                item._sec_get_downward_defined_userids_helper(d)
            for item in self.get_nonactive_publishables():
                item._sec_get_downward_defined_userids_helper(d)
            for item in self.get_assets():
                item._sec_get_downward_defined_userids_helper(d)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_userinfos_for_userids')
    def sec_get_userinfos_for_userids(self, userids):
        d = {}
        for userid in userids:
            d[userid] = self.sec_get_user_info(userid)
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
        while IContainer.isImplementedBy(parent):
            for group in parent.sec_get_local_defined_groups():
                groups[group] = 1
            parent = parent.aq_parent
        return groups.keys()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_roles_for_group')
    def sec_get_upward_roles_for_group(self, group):
        """Get the roles that a group has here, defined in a higer
        level of the tree.
        """
        parent = self.aq_inner.aq_parent
        roles = {}
        while IContainer.isImplementedBy(parent):
            for role in parent.sec_get_local_roles_for_group(group):
                roles[role] = 1
            parent = parent.aq_parent
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
        if IContainer.isImplementedBy(self):
            for item in self.get_ordered_publishables():
                item._sec_get_downward_defined_groups_helper(d)
            for item in self.get_nonactive_publishables():
                item._sec_get_downward_defined_groups_helper(d)
            for item in self.get_assets():
                item._sec_get_downward_defined_groups_helper(d)

    def sec_get_groupsmapping(self):
        """Return the groupmappings for this object.
        """
        return self.__ac_local_groups__
        
    def sec_get_or_create_groupsmapping(self):
        """Return the groupmappings for this object. Create one of currently
        no mapping exists.
        """
        if not groups_enabled:
            return None

        if not self.__ac_local_groups__:
            self.__ac_local_groups__ = ZGroupsMapping('acl_groups')
        return self.sec_get_groupsmapping()

    def sec_cleanup_groupsmapping(self):
        """If called, check to see whether any mappings are defined in the
        mappings object. If not, clear the __ac_local_groups__ attribute
        for efficiency.
        """
        if self.__ac_local_groups__:
            if not self.__ac_local_groups__.getMappings():
                self.__ac_local_groups__ = None

InitializeClass(Security)
