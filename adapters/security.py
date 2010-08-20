# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from collections import defaultdict

from five import grok
from zope.component import getUtility
from zope.event import notify

from Acquisition import aq_parent
from AccessControl import getSecurityManager
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permission import Permission
from Products.Silva.Security import UnauthorizedRoleAssignement
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo

from silva.core import interfaces
from silva.core.interfaces import events
from silva.core.interfaces.service import IMemberService


def silva_roles(roles):
    silva_roles = list(set(roles).intersection(roleinfo.ASSIGNABLE_ROLES_SET))
    silva_roles.sort(key=roleinfo.ASSIGNABLE_ROLES.index, reverse=True)
    return silva_roles

def is_role_greater(role1, role2):
    index = roleinfo.ASSIGNABLE_ROLES.index
    return index(role1) > index(role2)

def is_role_greater_or_equal(role1, role2):
    index = roleinfo.ASSIGNABLE_ROLES.index
    return index(role1) >= index(role2)

def minimum_role(role):
    all_roles = list(roleinfo.ALL_ROLES)
    return all_roles[all_roles.index(role):]


class AccessSecurityAdapter(grok.Adapter):
    grok.implements(interfaces.IAccessSecurity)
    grok.provides(interfaces.IAccessSecurity)
    grok.context(interfaces.ISilvaObject)

    def set_acquired(self):
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=(),
            acquire=1)
        notify(events.SecurityRestrictionModifiedEvent(self.context, None))

    def is_acquired(self):
        permission = Permission(SilvaPermissions.View, (), self.context)
        return isinstance(permission.getRoles(default=[]), list)

    def set_minimum_role(self, role):
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=minimum_role(role),
            acquire=0)
        notify(events.SecurityRestrictionModifiedEvent(self.context, role))

    def get_minimum_role(self):
        roles = filter(
            lambda r: r in roleinfo.ALL_ROLES,
            map(str, rolesForPermissionOn(
                    SilvaPermissions.View, self.context)))
        roles.sort(key=roleinfo.ALL_ROLES.index)
        if roles:
            role = roles[0]
            if role == 'Anonymous':
                return None
            return role
        return None

    minimum_role = property(get_minimum_role, set_minimum_role)
    acquired = property(is_acquired)


class RootAccessSecurityAdapter(AccessSecurityAdapter):
    grok.context(interfaces.IRoot)

    def set_acquired(self):
        # we're root, we can't set it to acquire, just give
        # everybody permission again
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=roleinfo.ALL_ROLES,
            acquire=0)
        notify(events.SecurityRestrictionModifiedEvent(self.context, None))

    def is_acquired(self):
        if not self.get_minimum_role():
            return True
        return AccessSecurityAdapter.is_acquired(self)

    # Need to redefined the property with the new version of is_acquired
    acquired = property(is_acquired)


class UserAuthorization(object):
    grok.implements(interfaces.IUserAuthorization)

    def __init__(self, context, query, member,
                 local_roles=[], acquired_roles=[]):
        self.context = context
        self.__query = query
        self.member = member
        self.__acquired_roles = silva_roles(acquired_roles)
        self.__local_roles = silva_roles(local_roles)

    @property
    def local_role(self):
        roles = self.__local_roles
        return roles[0] if len(roles) else None

    @property
    def acquired_role(self):
        roles = self.__acquired_roles
        return roles[0] if len(roles) else None

    @property
    def role(self):
        local_role = self.local_role
        acquired_role = self.acquired_role
        if local_role is None:
            return acquired_role
        if acquired_role is None:
            return local_role
        if is_role_greater(local_role, acquired_role):
            return local_role
        return acquired_role

    @property
    def username(self):
        return self.member.fullname()

    @property
    def userid(self):
        return self.member.userid()

    def revoke(self):
        """Revoke all Silva roles defined at this level for this user,
        if the current user have at least that role.
        """
        role = self.local_role
        if not role:
            return False
        user_id = self.userid
        user_role = self.__query.get_user_role()
        if user_role is None or is_role_greater(role, user_role):
            raise UnauthorizedRoleAssignement(role, user_id)
        self.context.manage_delLocalRoles([user_id])
        # Update computed value
        self.__local_roles = []
        notify(events.SecurityRoleRemovedEvent(self.context, user_id, []))
        return True

    def grant(self, role):
        """Grant a new role to the user, if it doesn't already have it
        The current user must have at least that role.
        """
        current_role = self.role
        if current_role and is_role_greater_or_equal(current_role, role):
            return False
        user_id = self.userid
        user_role = self.__query.get_user_role()
        if user_role is None or is_role_greater(role, user_role):
            raise UnauthorizedRoleAssignement(role, user_id)
        if role not in self.member.allowed_roles():
            raise UnauthorizedRoleAssignement(role, user_id)
        self.context.manage_addLocalRoles(user_id, [role])
        # Update computed value
        self.__local_roles.insert(0, role)
        notify(events.SecurityRoleAddedEvent(self.context, user_id, [role]))
        return True

    def __repr__(self):
        return '<UserAuthorization for %s in %r>' % (
            self.userid, self.context)


class UserAccess(grok.Adapter):
    grok.context(interfaces.ISilvaObject)
    grok.provides(interfaces.IUserAccessSecurity)
    grok.implements(interfaces.IUserAccessSecurity)

    def __init__(self, context):
        self.context = context
        self.__service = getUtility(IMemberService)

    def get_user_role(self, user_id=None):
        return self.get_user_authorization(user_id=user_id).role

    def __get_default_roles(self, user_id):
        user = self.context.acl_users.getUser(user_id)
        if user is not None:
            return user.getRoles()
        return []

    def get_user_authorization(self, user_id=None, dont_acquire=False):
        """Return authorization object for the given user. If no user
        is specified, return authorization object for the current
        authenticated user.
        """
        if user_id is None:
            user_id = getSecurityManager().getUser().getId()

        local_roles = self.context.get_local_roles_for_userid(user_id)

        acquired_roles = []
        if not dont_acquire:
            content = self.context
            while not interfaces.IRoot.providedBy(content):
                content = aq_parent(content)
                acquired_roles.extend(
                    content.get_local_roles_for_userid(user_id))
            acquired_roles.extend(
                self.__get_default_roles(user_id))

        return UserAuthorization(
            self.context,
            self,
            self.__service.get_member(user_id, location=self.context),
            local_roles,
            acquired_roles)

    def get_users_authorization(self, user_ids, dont_acquire=False):
        """Return all current authorizations at this level, and
        authorization objects for given users.
        """
        auth = {}
        for user_id in user_ids:
            if user_id not in auth:
                auth[user_id] = self.get_user_authorization(
                    user_id, dont_acquire=dont_acquire)
        return auth

    def get_defined_authorizations(self, dont_acquire=False):
        """Return current all authorizations at this level.
        """
        user_ids = set()
        local_roles = defaultdict(list)
        acquired_roles = defaultdict(list)

        # Collect user with roles here, tag as local_roles
        for user_id, roles in self.context.get_local_roles():
            user_ids.add(user_id)
            local_roles[user_id].extend(roles)

        if not dont_acquire:
            # Collect user with parent roles
            content = self.context
            while not interfaces.IRoot.providedBy(content):
                content = aq_parent(content)
                for user_id, roles in content.get_local_roles():
                    user_ids.add(user_id)
                    acquired_roles[user_id].extend(roles)

        auth = {}
        for user_id in user_ids:
            user_local_roles = silva_roles(local_roles[user_id])
            user_acquired_roles = silva_roles(acquired_roles[user_id])
            if not (user_local_roles or user_acquired_roles):
                # If the user doesn't have any Silva roles, we ignore it
                continue
            if not dont_acquire:
                # If we acquired default roles, add default user roles.
                user_acquired_roles.extend(
                    self.__get_default_roles(user_id))

            auth[user_id] = UserAuthorization(
                self.context,
                self,
                self.__service.get_member(user_id, location=self.context),
                user_local_roles,
                user_acquired_roles)

        return auth
