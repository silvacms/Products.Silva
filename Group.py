# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $
from AccessControl import ClassSecurityInfo, Unauthorized
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
        if self.isValid():
            # the real group is only deleted if the asset is valid
            self.service_groups.removeNormalGroup(self._group_name)
   
    def isValid(self):
        """returns whether the group asset is valid

            A group asset becomes invalid if it gets moved around ...
        """
        return (self.valid_path == self.getPhysicalPath())
        
    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'addUser')
    def addUser(self, userid):
        """adds user with given userid to group"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        self.service_groups.addUserToZODBGroup(userid, self._group_name)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'removeUser')
    def removeUser(self, userid):
        """removes user with given userid from group"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        self.service_groups.removeUserFromZODBGroup(userid, self._group_name)

    # ACCESSORS    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'listUsers')
    def listUsers(self):
        """ returns a (sorted) list of users in this group""" 
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
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
        raise AttributeError, "There is no service_groups"
    if self.service_groups.isGroup(group_name):
        raise ValueError, "There is already a group of that name."
    object = Group(id, title, group_name)
    self._setObject(id, object)
    object = getattr(self, id)
    # set the valid_path, this cannot be done in the constructor because the context
    # is not known as the object is not inserted into the container.
    object.valid_path = object.getPhysicalPath()
    self.service_groups.addNormalGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''

