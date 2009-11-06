# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$
import Globals, AccessControl, Products
from AccessControl import Permissions
from Products.Silva import roleinfo

# General Zope permissions
View = Permissions.view
AccessContentsInformation = Permissions.access_contents_information
UndoChanges = Permissions.undo_changes
ChangePermissions = Permissions.change_permissions
ViewManagementScreens = Permissions.view_management_screens
ManageProperties = Permissions.manage_properties
FTPAccess = Permissions.ftp_access

def setDefaultRoles(permission, roles):
    '''
    Sets the defaults roles for a permission. Borrowed from CMF.
    '''
    # XXX This ought to be in AccessControl.SecurityInfo.
    registered = AccessControl.Permission._registeredPermissions
    if not registered.has_key(permission):
        registered[permission] = 1
        Products.__ac_permissions__=(
            Products.__ac_permissions__+((permission,(),roles),))
        mangled = AccessControl.Permission.pname(permission)
        setattr(Globals.ApplicationDefaultPermissions, mangled, roles)
        
# Silva permissions
# XXX is ViewAuthenticated in use?
ViewAuthenticated = 'View Authenticated'
setDefaultRoles(ViewAuthenticated,
                ('Authenticated',) + roleinfo.ASSIGNABLE_ROLES)

ReadSilvaContent = 'Read Silva content'
setDefaultRoles(ReadSilvaContent, roleinfo.READER_ROLES)

ChangeSilvaContent = 'Change Silva content'
setDefaultRoles(ChangeSilvaContent, roleinfo.AUTHOR_ROLES)

ApproveSilvaContent = 'Approve Silva content'
setDefaultRoles(ApproveSilvaContent, roleinfo.EDITOR_ROLES)

ChangeSilvaAccess = 'Change Silva access'
setDefaultRoles(ChangeSilvaAccess, roleinfo.CHIEF_ROLES)

