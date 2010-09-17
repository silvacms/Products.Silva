# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from AccessControl import ClassSecurityInfo, getSecurityManager
from Acquisition import aq_base
from App.class_init import InitializeClass
from DateTime import DateTime

from zope.component import getUtility

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva.AccessManager import AccessManager
from Products.Silva.Membership import noneMember

from silva.core.interfaces import IVersion, IRoot
from silva.core.services.interfaces import IMemberService

from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaMetadata.Exceptions import BindingError

# LOCK_DURATION = (1./24./60.)*20. # 20 minutes, expressed as fraction of a day


class SecurityError(Exception):
    """An error has been triggered by the security system.
    """

class UnauthorizedRoleAssignement(SecurityError):
    """This roles can be assigned.
    """

class Security(AccessManager):
    """Can be mixed in with an object to support Silva security.
    (built on top of Zope security)
    Methods prefixed with sec_ so as not to disrupt similarly named
    Zope's security methods. (ugly..)
    """
    security = ClassSecurityInfo()

    _last_author_userid = None
    _last_author_info = None
    # _lock_info = None

    # MANIPULATORS
    # security.declareProtected(SilvaPermissions.ChangeSilvaContent,
    #                           'sec_have_management_rights')
    # def sec_have_management_rights(self):
    #     """Check whether we have management rights here.
    #     """
    #     return getSecurityManager().getUser().has_role(['Manager'], self)


    # security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
    #                           'sec_assign')
    # def sec_assign(self, userid, role):
    #     """Assign role to userid for this object.
    #     """

    #     member = self.sec_get_member(userid)
    #     if role not in member.allowed_roles():
    #         raise UnauthorizedRoleAssignement
    #     self.manage_addLocalRoles(userid, [role])
    #     notify(SecurityRoleAddedEvent(self, userid, [role]))

    # security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
    #                           'sec_remove')
    # def sec_remove(self, userid):
    #     """Remove a user completely from this object.
    #     """
    #     # FIXME: should this check for non Silva roles and keep
    #     # user if they exist?
    #     # can't remove managers if we don't have the rights to do so
    #     if ('Manager' in self.sec_get_roles_for_userid(userid) and
    #         not self.sec_have_management_rights()):
    #         return
    #     self.manage_delLocalRoles([userid])
    #     notify(SecurityRoleRemovedEvent(self, userid, []))

    # security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
    #                           'sec_revoke')
    # def sec_revoke(self, userid, revoke_roles):
    #     """Remove roles from user in this object.
    #     """
    #     for role in revoke_roles:
    #         if role not in roleinfo.ASSIGNABLE_ROLES:
    #             return
    #         # can't revoke manager roles if we're not manager
    #         if (role == 'Manager' and
    #             not self.sec_have_management_rights()):
    #             return
    #     old_roles = self.get_local_roles_for_userid(userid)
    #     roles = [role for role in old_roles if role not in revoke_roles]
    #     if len(roles) > 0:
    #         self.manage_setLocalRoles(userid, roles)
    #     else:
    #         # if no more roles, remove user completely
    #         self.sec_remove(userid)
    #     notify(SecurityRoleRemovedEvent(self, userid, revoke_roles))

    # security.declareProtected(SilvaPermissions.ChangeSilvaContent,
    #                           'sec_create_lock')
    # def sec_create_lock(self):
    #     """Create lock for this object. Return true if successful.
    #     """
    #     if self.sec_is_locked():
    #         return 0
    #     user_id = getSecurityManager().getUser().getId()
    #     dt = DateTime()
    #     self._lock_info = user_id, dt
    #     return 1

    # security.declareProtected(SilvaPermissions.ChangeSilvaContent,
    #                           'sec_break_lock')
    # def sec_break_lock(self):
    #     """Breaks the lock.
    #     """
    #     self._lock_info = None

    # security.declareProtected(SilvaPermissions.ChangeSilvaContent,
    #                           'sec_is_locked')
    # def sec_is_locked(self):
    #     """Check whether this object is locked by a user currently
    #     editing.
    #     """
    #     if self._lock_info is None:
    #         return 0
    #     user_id, dt = self._lock_info
    #     current_dt = DateTime()
    #     if current_dt - dt >= LOCK_DURATION:
    #         return 0
    #     current_user_id = getSecurityManager().getUser().getId()
    #     return user_id != current_user_id


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

    # security.declareProtected(
    #     SilvaPermissions.ReadSilvaContent, 'sec_get_roles')
    # def sec_get_roles(self):
    #     """Get all roles defined here that we can manage, given the
    #     roles of this user.
    #     """
    #     return roleinfo.ASSIGNABLE_ROLES

    # security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
    #                           'sec_find_users')
    # def sec_find_users(self, search_string):
    #     """Find users in user database. This method delegates to
    #     service_members for security reasons.
    #     """
    #     # XXX this loop seems useless, why is it here? (maybe we need a copy?)
    #     members = []
    #     for member in self.service_members.find_members(search_string, location=self):
    #         members.append(member)
    #     return members

    # security.declareProtected(SilvaPermissions.ChangeSilvaAccess,
    #                           'sec_can_find_users')
    # def sec_can_find_users(self):
    #     """Tells if you can use sec_can_find_users. This method delegates to
    #     service_members for security reasons.
    #     """
    #     use_direct_lookup = getattr(self.service_members.aq_inner, 'use_direct_lookup', None)
    #     if use_direct_lookup is None:
    #         return False
    #     return use_direct_lookup()

    # security.declareProtected(SilvaPermissions.ReadSilvaContent,
    #                           'sec_get_member')
    # def sec_get_member(self, userid):
    #     """Get information for userid. This method delegates to
    #     service_members for security reasons.
    #     """
    #     return self.service_members.get_cached_member(userid, location=self)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'sec_get_last_author_info')
    def sec_get_last_author_info(self, version=None):
        """Get the info of the last author of the
           passed in version (this is a IMember object)
           if version is none, get the info for the
           previewable version.
        """
        #the version parameter was added to support
        # getting the last author info for the correct
        # version in the silva-extra metadata
        # (this was always returning the previewable
        # version's info, even if the version in question
        # was the published or closed version

        # get cached author info (may be None)
        if not version:
            version = self.get_previewable()
        if not (version or IVersion.providedBy(self)):
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
            user_id = getSecurityManager().getUser().getId()
            member = getUtility(IMemberService)
            user = member.get_cached_member(user_id, location=self)
            version._last_author_userid = user_id
            version._last_author_info = aq_base(user)
            binding = getUtility(IMetadataService).getMetadata(version)
            if binding is None:
                return
            now = DateTime()
            binding.setValues('silva-extra', {'modificationtime': now})

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_get_creator_info')
    def sec_get_creator_info(self):
        service = getUtility(IMemberService)
        user_id = self.getOwner().getId()
        return service.get_cached_member(user_id, location=self)

    # security.declareProtected(
    #     SilvaPermissions.ChangeSilvaAccess, 'sec_get_local_defined_userids')
    # def sec_get_local_defined_userids(self):
    #     """Get the list of userids with locally defined roles
    #     """
    #     result = []
    #     for userid, roles in self.get_local_roles():
    #         for role in roles:
    #             if role in roleinfo.ASSIGNABLE_ROLES:
    #                 result.append(userid)
    #                 break
    #     return result

    # security.declareProtected(
    #     SilvaPermissions.AccessContentsInformation, 'sec_get_local_roles_for_userid')
    # def sec_get_local_roles_for_userid(self, userid):
    #     """Get a list of local roles that a userid has here
    #     """
    #     return [role for role in self.get_local_roles_for_userid(userid)
    #             if role in roleinfo.ASSIGNABLE_ROLES]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'sec_get_all_roles')
    def sec_get_all_roles(self, userid=None):
        """Returns all roles the user has in this context.  If userid
        is None, then return all roles for the currently logged in
        user
        """
        roles = []
        if not userid:
            user = getSecurityManager().getUser()
        else:
            user = self.acl_users.getUser(userid)
        for role in roleinfo.ASSIGNABLE_ROLES[:]:
            if user.has_role(role, self):
                roles.append(role)
        return roles

    # security.declareProtected(
    #     SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_defined_userids')
    # def sec_get_upward_defined_userids(self):
    #     """Get the list of userids with roles defined in a higer
    #     level of the tree
    #     """
    #     userids = {}
    #     parent = self.aq_inner.aq_parent
    #     while IContainer.providedBy(parent):
    #         for userid in parent.sec_get_local_defined_userids():
    #             userids[userid] = 1
    #         parent = parent.aq_inner.aq_parent
    #     return userids.keys()

    # security.declareProtected(
    #     SilvaPermissions.ChangeSilvaAccess, 'sec_get_upward_roles_for_userid')
    # def sec_get_upward_roles_for_userid(self, userid):
    #     """Get the roles that a userid has here, defined in a higer
    #     level of the tree
    #     """
    #     roles = {}
    #     parent = self.aq_inner.aq_parent
    #     while IContainer.providedBy(parent):
    #         for role in parent.sec_get_local_roles_for_userid(userid):
    #             roles[role] = 1
    #         parent = parent.aq_inner.aq_parent
    #     return roles.keys()

    # security.declareProtected(
    #     SilvaPermissions.ChangeSilvaAccess, 'sec_get_members_for_userids')
    # def sec_get_members_for_userids(self, userids):
    #     d = {}

    #     for userid in userids:
    #         d[userid] = self.sec_get_member(userid)
    #     return d

InitializeClass(Security)
