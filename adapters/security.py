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


class ViewerSecurityAdapter(grok.Adapter):

    grok.implements(interfaces.IViewerSecurity)
    grok.context(interfaces.ISilvaObject)

    def setAcquired(self):
        # if we're root, we can't set it to acquire, just give
        # everybody permission again
        if interfaces.IRoot.providedBy(self.context):
            self.context.manage_permission(
                SilvaPermissions.View,
                roles=roleinfo.ALL_ROLES,
                acquire=0)
        else:
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
        if interfaces.IRoot.providedBy(self.context):
            return 'Anonymous'
        else:
            parent = aq_parent(aq_inner(self.context))
            return interfaces.IViewerSecurity(parent).getMinimumRole()

