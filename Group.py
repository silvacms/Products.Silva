# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.10 $
from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

# Silva interfaces
from ISilvaObject import ISilvaObject
# Silva
from SilvaObject import SilvaObject
import SilvaPermissions
# misc
from helpers import add_and_edit
try:
    from Products.Groups.GroupsErrors import GroupsError, BeforeDeleteException
except ImportError, ie:
    pass

icon = "www/group.png"

class Group(SilvaObject, SimpleItem):
    security = ClassSecurityInfo()

    meta_type = "Silva Group"

    __implements__ = ISilvaObject

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
    ) + SimpleItem.manage_options
    
    manage_main = PageTemplateFile('www/groupEdit', globals())

    def __init__(self, id, title, group_name):
        Group.inheritedAttribute('__init__')(self, id, title)
        self._group_name = group_name
        
    def manage_beforeDelete(self, item, container):        
        Group.inheritedAttribute('manage_beforeDelete')(self, item, container)
        if self.isValid():
            ## the real group is only deleted if the asset is valid
            #try:
            self.service_groups.removeNormalGroup(self._group_name)        
            #except GroupsError, ge:
            #    # Raise a BeforeDeleteException to get the deletion canceled.
            #    raise BeforeDeleteException, ge
   
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'isValid')
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
        SilvaPermissions.ChangeSilvaAccess, 'copyUsersFromGroup')
    def copyUsersFromGroups(self, groups):
        """copy users from other groups to this group"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        return self._copyUsersFromGroupsHelper(groups)

    def _copyUsersFromGroupsHelper(self, groups):
        sg = self.service_groups
        users = {}
        for group in groups:        
            if sg.isVirtualGroup(group):
                self._copyUsersFromGroupsHelper(sg.listGroupsInVirtualGroup(group))
            elif sg.isNormalGroup(group):
                for user in sg.listUsersInZODBGroup(group):
                    users[user] = 1
        userids = users.keys()
        for userid in userids:
            self.addUser(userid)
        # For UI feedback
        return userids

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
def manage_addGroup(self, id, title, group_name, asset_only=0, REQUEST=None):
    """Add a Group."""
    if not asset_only:
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
    if not asset_only:
        self.service_groups.addNormalGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''

