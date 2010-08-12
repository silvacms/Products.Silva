# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.event import notify

from Acquisition import aq_parent, aq_inner
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permission import Permission
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo

from types import ListType

from silva.core import interfaces
from silva.core.interfaces import events


class AccessSecurityAdapter(grok.Adapter):
    grok.implements(interfaces.IAccessSecurity)
    grok.provides(interfaces.IAccessSecurity)
    grok.context(interfaces.ISilvaObject)

    def setAcquired(self):
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=(),
            acquire=1)
        notify(events.SecurityRestrictionModifiedEvent(self.context, None))

    def setMinimumRole(self, role):
        if role == 'Anonymous':
            self.setAcquired()
        else:
            self.context.manage_permission(
                SilvaPermissions.View,
                roles=roleinfo.getRolesAbove(role),
                acquire=0)
            notify(events.SecurityRestrictionModifiedEvent(self.context, role))

    def isAcquired(self):
        if (interfaces.IRoot.providedBy(self.context) and
            self.getMinimumRole() == 'Anonymous'):
            return 1
        # it's unbelievable, but that's the Zope API..
        p = Permission(SilvaPermissions.View, (), self.context)
        return type(p.getRoles(default=[])) is ListType

    def getMinimumRole(self):
        # XXX this only works if rolesForPermissionOn returns roles
        # in definition order..
        return str(rolesForPermissionOn(
            SilvaPermissions.View, self.context)[0])

    def getMinimumRoleAbove(self):
        parent = aq_parent(aq_inner(self.context))
        return interfaces.IAccessSecurity(parent).getMinimumRole()


class RootAccessSecurityAdapter(AccessSecurityAdapter):
    grok.context(interfaces.IRoot)

    def setAcquired(self):
        # we're root, we can't set it to acquire, just give
        # everybody permission again
        self.context.manage_permission(
            SilvaPermissions.View,
            roles=roleinfo.ALL_ROLES,
            acquire=0)
        notify(events.SecurityRestrictionModifiedEvent(self.context, None))

    def getMinimumRoleAbove(self):
        return 'Anonymous'


class UserAuthorization(object):
    grok.implements(interfaces.IUserAuthorization)

    def __init__(self, userid):
        self.userid = userid
        self.acquired_roles = []
        self.local_roles = []


class UserAccess(grok.Adapter):
    grok.context(interfaces.ISilvaObject)
    grok.provides(interfaces.IUserAccessSecurity)
    grok.implements(interfaces.IUserAccessSecurity)

    def getAuthorizations(self):
        auth = {}
        # Collect user with roles here, tag as local_roles
        for userid, roles in self.context.get_local_roles():
            if userid not in auth:
                auth[userid] = UserAuthorization(userid)
            user_auth = auth[userid]
            for role in roles:
                if role in roleinfo.ASSIGNABLE_ROLES:
                    user_auth.local_roles.append(role)

        # Collect user with parent roles
        content = self.context
        while not interfaces.IRoot.providedBy(content):
            content = aq_parent(content)
            for userid, roles in content.get_local_roles():
                if userid not in auth:
                    auth[userid] = UserAuthorization(userid)
                user_auth = auth[userid]
                for role in roles:
                    if role in roleinfo.ASSIGNABLE_ROLES:
                        user_auth.acquired_roles.append(role)

        return auth
