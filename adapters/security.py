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


def sanatize_roles(roles):
    silva_roles = list(set(roles).intersection(roleinfo.ASSIGNABLE_ROLES_SET))
    silva_roles.sort(key=roleinfo.ASSIGNABLE_ROLES.index, reverse=True)
    return silva_roles

def is_role_greater(role1, role2):
    index = roleinfo.ASSIGNABLE_ROLES.index
    return index(role1) > index(role2)

def is_role_greater_or_equal(role1, role2):
    index = roleinfo.ASSIGNABLE_ROLES.index
    return index(role1) >= index(role2)

def required_roles_for_role(role):
    all_roles = list(roleinfo.ASSIGNABLE_ROLES)
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

    def set_role(self, role):
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=required_roles_for_role(role),
            acquire=0)
        notify(events.SecurityRestrictionModifiedEvent(self.context, role))

    def get_role(self):
        roles = filter(
            lambda r: r in roleinfo.ASSIGNABLE_ROLES,
            map(str, rolesForPermissionOn(
                    SilvaPermissions.View, self.context)))
        roles.sort(key=roleinfo.ASSIGNABLE_ROLES.index)
        if roles:
            return roles[0]
        return None

    role = property(get_role, set_role)
    acquired = property(is_acquired)


class RootAccessSecurityAdapter(AccessSecurityAdapter):
    grok.context(interfaces.IRoot)

    def set_acquired(self):
        # we're root, we can't set it to acquire, just give
        # everybody permission again
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=('Anonymous',),
            acquire=0)
        notify(events.SecurityRestrictionModifiedEvent(self.context, None))

    def is_acquired(self):
        if not self.get_role():
            return True
        return AccessSecurityAdapter.is_acquired(self)


class UserAuthorization(object):
    grok.implements(interfaces.IUserAuthorization)

    def __init__(self, context, query, user,
                 local_roles=[], acquired_roles=[]):
        self.context = context
        self.query = query
        self.__user = user
        self.__acquired_roles = sanatize_roles(acquired_roles)
        self.__local_roles = sanatize_roles(local_roles)

    @property
    def all_local_roles(self):
        return self.__local_roles

    @property
    def all_acquired_roles(self):
        return self.__acquired_roles

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
        return self.__user.fullname()

    @property
    def userid(self):
        return self.__user.userid()

    def revoke(self):
        """Revoke all Silva roles defined at this level for this user,
        if the current user have at least that role.
        """
        role = self.local_role
        if not role:
            return False
        user_id = self.userid
        if is_role_greater(role, self.query.get_user_role()):
            raise UnauthorizedRoleAssignement(role, user_id)
        self.context.manage_delLocalRoles([user_id])
        notify(events.SecurityRoleRemovedEvent(self.context, user_id, []))
        return True

    def grant(self, role):
        """Grant a new role to the user, if it doesn't already have it
        The current user must have at least that role.
        """
        user_role = self.role
        if user_role and is_role_greater_or_equal(user_role, role):
            return False
        user_id = self.userid
        if is_role_greater(role, self.query.get_user_role()):
            raise UnauthorizedRoleAssignement(role, user_id)
        if role not in self.__user.allowed_roles():
            raise UnauthorizedRoleAssignement(role, user_id)
        self.context.manage_addLocalRoles(user_id, [role])
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

    def get_user_authorization(self, user_id=None):
        """Return authorization object for the given user. If no user
        is specified, return authorization object for the current
        authenticated user.
        """
        if user_id is None:
            user_id = getSecurityManager().getUser().getId()

        local_roles = self.context.get_local_roles_for_userid(user_id)

        acquired_roles = []
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

    def get_authorizations_for(self, user_ids):
        """Return all current authorizations at this level, and
        authorization objects for given users.
        """
        auth = self.get_authorizations()
        for user_id in user_ids:
            if user_id not in auth:
                auth[user_id] = UserAuthorization(
                    self.context,
                    self,
                    self.__service.get_member(
                        user_id, location=self.context),
                    [],
                    self.__get_default_roles(user_id))
        return auth

    def get_authorizations(self):
        """Return current all authorizations at this level.
        """
        user_ids = set()
        local_roles = defaultdict(list)
        acquired_roles = defaultdict(list)

        # Collect user with roles here, tag as local_roles
        for user_id, roles in self.context.get_local_roles():
            user_ids.add(user_id)
            local_roles[user_id].extend(roles)

        # Collect user with parent roles
        content = self.context
        while not interfaces.IRoot.providedBy(content):
            content = aq_parent(content)
            for user_id, roles in content.get_local_roles():
                user_ids.add(user_id)
                acquired_roles[user_id].extend(roles)

        auth = {}
        for user_id in user_ids:
            acquired_roles[user_id].extend(
                self.__get_default_roles(user_id))

            auth[user_id] = UserAuthorization(
                self.context,
                self,
                self.__service.get_member(user_id, location=self.context),
                local_roles[user_id],
                acquired_roles[user_id])

        return auth
