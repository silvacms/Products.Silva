# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from collections import defaultdict

from five import grok
from zope import interface
from zope.component import getUtility, queryUtility
from zope.event import notify

from Acquisition import aq_parent
from AccessControl import getSecurityManager
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permission import Permission
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo

from silva.core import interfaces
from silva.core.interfaces import events, errors
from silva.core.services.interfaces import IMemberService, IGroupService
from silva.translations import translate as _


def silva_roles(roles):
    """This method returns only roles used by Silva from the given
    list, sorted in order of importance.
    """
    if roles is None:
        return []
    silva_roles = list(set(roles).intersection(roleinfo.ASSIGNABLE_ROLES_SET))
    silva_roles.sort(key=roleinfo.ASSIGNABLE_ROLES.index, reverse=True)
    return silva_roles

def is_role_greater(role1, role2):
    index = roleinfo.ASSIGNABLE_ROLES.index
    try:
        return index(role1) > index(role2)
    except ValueError:
        return False

def is_role_greater_or_equal(role1, role2):
    index = roleinfo.ASSIGNABLE_ROLES.index
    try:
        return index(role1) >= index(role2)
    except ValueError:
        return False

def minimum_role(role):
    all_roles = list(roleinfo.ALL_ROLES)
    return all_roles[all_roles.index(role):]


class AccessSecurityManager(grok.Adapter):
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


class RootAccessSecurityAdapter(AccessSecurityManager):
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
        return AccessSecurityManager.is_acquired(self)

    # Need to redefined the property with the new version of is_acquired
    acquired = property(is_acquired)


class Authorization(object):
    grok.implements(interfaces.IAuthorization)

    def __init__(
        self, context, query, identifier, name, type, source,
        local_roles=None, acquired_roles=None):
        self.identifier = identifier
        self.name = name
        self.type = type
        self.source = source
        self.context = context
        self._query = query
        self._acquired_roles = silva_roles(acquired_roles)
        self._local_roles = silva_roles(local_roles)

    @property
    def email(self):
        if not interfaces.IMember.providedBy(self.source):
            return None
        return self.source.email()

    @property
    def local_role(self):
        roles = self._local_roles
        return roles[0] if len(roles) else None

    @property
    def acquired_role(self):
        roles = self._acquired_roles
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

    def revoke(self):
        """Revoke all Silva roles defined at this level for this user,
        if the current user have at least that role.
        """
        role = self.local_role
        if not role:
            return False
        identifier = self.identifier
        if identifier == self._query.get_user_id():
            raise errors.UnauthorizedRoleAssignement(
                _(u"You cannot revoke your own role"),
                self.context, role, identifier)
        user_role = self._query.get_user_role()
        if user_role is None or is_role_greater(role, user_role):
            raise errors.UnauthorizedRoleAssignement(
                _(u"You must have at least the role you are trying to revoke"),
                self.context, role, identifier)
        self.context.manage_delLocalRoles([identifier])
        # Update computed value
        self._local_roles = []
        notify(events.SecurityRoleRemovedEvent(self.context, identifier, []))
        return True

    def grant(self, role):
        """Grant a new role to the user, if it doesn't already have it
        The current user must have at least that role.
        """
        current_role = self.role
        if current_role and is_role_greater_or_equal(current_role, role):
            return False
        identifier = self.identifier
        user_role = self._query.get_user_role()
        if user_role is None or is_role_greater(role, user_role):
            raise errors.UnauthorizedRoleAssignement(
                _(u"You must have at least the role you are trying to grant"),
                self.context, role, identifier)
        if role not in self.source.allowed_roles():
            raise errors.UnauthorizedRoleAssignement(
                _(u"This role cannot be granted in this context"),
                self.context, role, identifier)
        self.context.manage_setLocalRoles(identifier, [role])
        # Update computed value
        self._local_roles.insert(0, role)
        notify(events.SecurityRoleAddedEvent(self.context, identifier, [role]))
        return True

    def __repr__(self):
        return '<Authorization for %s %s in %r>' % (
            self.type, self.identifier, self.context)


class IAuthorizationFactory(interface.Interface):

    def __call__(context, query, local_roles=None, acquired_roles=None):
        """Return a new IAuthorization.
        """


class UserAuthorizationFactory(grok.Adapter):
    grok.provides(IAuthorizationFactory)
    grok.context(interfaces.IMember)

    def __init__(self, member):
        self.member = member

    def get_default_roles(self, context, user_id):
        user = context.acl_users.getUser(user_id)
        if user is not None:
            return user.getRoles()
        return []

    def __call__(self, context, query, local_roles=None, acquired_roles=None):
        identifier = self.member.userid()
        name = self.member.fullname()
        if acquired_roles is not None:
            acquired_roles.extend(self.get_default_roles(context, identifier))
        return Authorization(
            context, query, identifier, name, 'user', self.member,
            local_roles, acquired_roles)


class GroupAuthorizationFactory(grok.Adapter):
    grok.provides(IAuthorizationFactory)
    grok.context(interfaces.IGroup)

    def __init__(self, group):
        self.group = group

    def __call__(self, context, query, local_roles=None, acquired_roles=None):
        identifier = self.group.groupid()
        name = self.group.groupname()
        return Authorization(
            context, query, identifier, name, 'group', self.group,
            local_roles, acquired_roles)


class AuthorizationManager(grok.Adapter):
    grok.context(interfaces.ISilvaObject)
    grok.provides(interfaces.IAuthorizationManager)
    grok.implements(interfaces.IAuthorizationManager)

    def __init__(self, context):
        self.context = context
        self._current_user_id = getSecurityManager().getUser().getId()
        self._member = getUtility(IMemberService)
        self._group = queryUtility(IGroupService)

    def get_user_role(self, identifier=None):
        authorization = self.get_authorization(identifier=identifier)
        if authorization is None:
            return None
        return authorization.role

    def get_user_id(self, identifier=None):
        if identifier is None:
            return self._current_user_id
        return identifier

    def _get_identity(self, identifier):
        identity = self._member.get_member(identifier, location=self.context)
        if identity is None and self._group is not None:
            identity = self._group.get_group(identifier, location=self.context)
        return identity

    def get_authorization(self, identifier=None, dont_acquire=False):
        """Return authorization object for the given user. If no user
        is specified, return authorization object for the current
        authenticated user.
        """
        identifier = self.get_user_id(identifier)

        identity = self._get_identity(identifier)
        if identity is None:
            return None
        local_roles = self.context.get_local_roles_for_userid(identifier)

        acquired_roles = None
        if not dont_acquire:
            acquired_roles = []
            content = self.context
            while not interfaces.IRoot.providedBy(content):
                content = aq_parent(content)
                acquired_roles.extend(
                    content.get_local_roles_for_userid(identifier))

        return IAuthorizationFactory(identity)(
            self.context, self, local_roles, acquired_roles)

    def get_authorizations(self, identifiers, dont_acquire=False):
        """Return all current authorizations at this level, and
        authorization objects for given users/groups or other.
        """
        authorizations = {}
        for identifier in identifiers:
            if identifier not in authorizations:
                authorization = self.get_authorization(
                    identifier, dont_acquire=dont_acquire)
                if authorization is not None:
                    authorizations[identifier] = authorization
        return authorizations

    def get_defined_authorizations(self, dont_acquire=False):
        """Return current all authorizations at this level.
        """
        identifiers = set()
        local_roles = defaultdict(list)
        acquired_roles = defaultdict(list)

        # Collect user with roles here, tag as local_roles
        for identifier, roles in self.context.get_local_roles():
            identifiers.add(identifier)
            local_roles[identifier].extend(roles)

        if not dont_acquire:
            # Collect user with parent roles
            content = self.context
            while not interfaces.IRoot.providedBy(content):
                content = aq_parent(content)
                for identifier, roles in content.get_local_roles():
                    identifiers.add(identifier)
                    acquired_roles[identifier].extend(roles)

        auth = {}
        for identifier in identifiers:
            identity = self._get_identity(identifier)
            if identity is None:
                continue
            identity_local_roles = silva_roles(local_roles[identifier])
            identity_acquired_roles = silva_roles(acquired_roles[identifier])
            if not (identity_local_roles or identity_acquired_roles):
                # If the user doesn't have any Silva roles, we ignore it
                continue
            if dont_acquire:
                identity_acquired_roles = None

            auth[identifier] = IAuthorizationFactory(identity)(
                self.context,
                self,
                identity_local_roles,
                identity_acquired_roles)

        return auth
