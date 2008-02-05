# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.21 $
from zope.interface import implements

from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem

# Silva
from SilvaObject import SilvaObject
from Products.Silva import mangle
import SilvaPermissions
# misc
from helpers import add_and_edit
try:
    from Products.Groups.GroupsErrors import GroupsError, BeforeDeleteException
except ImportError, ie:
    pass

from interfaces import ISilvaObject, IGroup

class Group(SilvaObject, SimpleItem):
    """Silva Group"""
    security = ClassSecurityInfo()

    meta_type = "Silva Group"

    implements(IGroup)

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
    ) + SimpleItem.manage_options
    
    manage_main = PageTemplateFile('www/groupEdit', globals())

    def __init__(self, id, group_name):
        Group.inheritedAttribute('__init__')(self, id)
        self._group_name = group_name
        
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
        SilvaPermissions.ChangeSilvaAccess, 'copyUsersFromGroups')
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
                self._copyUsersFromGroupsHelper(
                    sg.listGroupsInVirtualGroup(group))
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

def manage_addGroup(self, id, title, group_name, asset_only=0, REQUEST=None):
    """Add a Group."""
    if not asset_only:
        if not mangle.Id(self, id).isValid():
            return
        # these checks should also be repeated in the UI
        if not hasattr(self, 'service_groups'):
            raise AttributeError, "There is no service_groups"
        if self.service_groups.isGroup(group_name):
            raise ValueError, "There is already a group of that name."
    object = Group(id, group_name)
    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    # set the valid_path, this cannot be done in the constructor because the context
    # is not known as the object is not inserted into the container.
    object.valid_path = object.getPhysicalPath()
    if not asset_only:
        self.service_groups.addNormalGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''

def group_will_be_removed(group, event):        
    if group.isValid() and hasattr(group, 'service_groups'):
        group.service_groups.removeNormalGroup(group._group_name)        
