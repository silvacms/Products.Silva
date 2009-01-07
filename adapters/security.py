# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: security.py,v 1.10 2006/01/24 16:12:01 faassen Exp $
#
from zope.interface import implements

import Globals
from Acquisition import aq_parent, aq_inner
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo,\
     getSecurityManager
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permission import Permission
from Products.Silva import SilvaPermissions
from Products.Silva import roleinfo
from Products.Silva import interfaces as silva_interfaces
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

from DateTime import DateTime
from types import ListType

class ViewerSecurityAdapter(object):
    implements(interfaces.IViewerSecurity)

    def __init__(self, context):
        self.context = context
        
    def setAcquired(self):
        # if we're root, we can't set it to acquire, just give
        # everybody permission again
        if silva_interfaces.IRoot.providedBy(self.context):
            self.context.manage_permission(
                SilvaPermissions.View,
                roles=roleinfo.ALL_ROLES,
                acquire=0)
        else:
            self.context.manage_permission(
                SilvaPermissions.View,
                roles=(),
                acquire=1)
    
    def setMinimumRole(self, role):
        if role == 'Anonymous':
            self.setAcquired()
        else:
            self.context.manage_permission(
                SilvaPermissions.View,
                roles=roleinfo.getRolesAbove(role),
                acquire=0)

    def isAcquired(self):
        if (silva_interfaces.IRoot.providedBy(self.context) and
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
        if silva_interfaces.IRoot.providedBy(self.context):
            return 'Anonymous'
        else:
            parent = aq_parent(aq_inner(self.context))
            return interfaces.IViewerSecurity(parent).getMinimumRole()

# XXX in the future we want to define a getAdapter
# ViewerSecurityAdapter should then be defined for every ISilvaObject
# (probably we'd define another adapter on IRoot and refactor this one)

# 20 minutes, expressed as a fraction of a day
LOCK_DURATION = (1./24./60.)*20.

# XXX this adapter still depends on variable _lock_info being defined
# on the Security mixin.

class LockAdapter(adapter.Adapter):
    implements(interfaces.ILockable)
        
    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'createLock')
    def createLock(self):
        if self.isLocked():
            return 0
        user_id = getSecurityManager().getUser().getId()
        dt = DateTime()
        self.context._lock_info = user_id, dt
        return 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'breakLock')
    def breakLock(self):
        self.context._lock_info = None

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'isLocked')
    def isLocked(self):
        if self.context._lock_info is None:
            return 0
        user_id, dt = self.context._lock_info
        current_dt = DateTime()
        if current_dt - dt >= LOCK_DURATION:
            return 0
        current_user_id = getSecurityManager().getUser().getId()
        return user_id != current_user_id

Globals.InitializeClass(LockAdapter)

def getLockAdapter(context):
    return LockAdapter(context).__of__(context)
