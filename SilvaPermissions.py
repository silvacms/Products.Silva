# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.7 $
import Globals, AccessControl, Products
from AccessControl import Permissions

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
ReadSilvaContent = 'Read Silva content'
setDefaultRoles(ReadSilvaContent, ('Manager', 'ChiefEditor',
                                   'Editor', 'Author', 'Reader'))

ChangeSilvaContent = 'Change Silva content'
setDefaultRoles(ChangeSilvaContent, ('Manager', 'ChiefEditor',
                                     'Editor', 'Author'))

ApproveSilvaContent = 'Approve Silva content'
setDefaultRoles(ApproveSilvaContent, ('Manager', 'ChiefEditor', 'Editor'))

ChangeSilvaAccess = 'Change Silva access'
setDefaultRoles(ChangeSilvaAccess, ('Manager', 'ChiefEditor'))

ChangeSilvaViewRegistry = 'Change Silva View Registry'
setDefaultRoles(ChangeSilvaViewRegistry, ('Manager',))
