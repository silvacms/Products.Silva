# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.2 $
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva interfaces
from IAsset import IAsset
# Silva
from Asset import Asset
import SilvaPermissions
# misc
from helpers import add_and_edit

class Group(Asset):
    security = ClassSecurityInfo()

    meta_type = "Silva Group"

    __implements__ = IAsset

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
    ) + Asset.manage_options

    manage_main = PageTemplateFile('www/groupEdit', globals())


    def __init__(self, id, title, group_name):
        Group.inheritedAttribute('__init__')(self, id, title)
        self._group_name = group_name
        
    def manage_beforeDelete(self, item, container):
        Group.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.service_groups.removeNormalGroup(self._group_name)
        
    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'addUser')
    def addUser(self, userid):
        self.service_groups.addUserToZODBGroup(userid, self._group_name)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'removeUser')
    def removeUser(self, userid):
        self.service_groups.removeUserFromZODBGroup(userid, self._group_name)

    # ACCESSORS    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'listUsers')
    def listUsers(self):
        result = self.service_groups.listUsersInZODBGroup(self._group_name)
        result.sort()
        return result

InitializeClass(Group)

manage_addGroupForm = PageTemplateFile("www/groupAdd", globals(),
                                       __name__='manage_addGroupForm')
def manage_addGroup(self, id, title, group_name, REQUEST=None):
    """Add a Group."""
    if not self.is_id_valid(id):
        return
    # these checks should also be repeated in the UI
    if not hasattr(self, 'service_groups'):
        return
    if self.service_groups.isGroup(group_name):
        return
    object = Group(id, title, group_name)
    self._setObject(id, object)
    object = getattr(self, id)
    self.service_groups.addNormalGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''

