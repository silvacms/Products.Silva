# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import Permissions

# General Zope permissions
View = Permissions.view
AccessContentsInformation = Permissions.access_contents_information
UndoChanges = Permissions.undo_changes
ChangePermissions = Permissions.change_permissions
ViewManagementScreens = Permissions.view_management_screens
ManageProperties = Permissions.manage_properties
FTPAccess = Permissions.ftp_access

# Some silva permissions
ReadSilvaContent = 'Read Silva content'
ChangeSilvaContent = 'Change Silva content'
ApproveSilvaContent = 'Approve Silva content'
ChangeSilvaAccess = 'Change Silva access'
