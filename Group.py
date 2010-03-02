# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo, Unauthorized
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS.interfaces

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva.SilvaObject import SilvaObject
from Products.Silva.helpers import add_and_edit

from silva.core import interfaces
from silva.core import conf as silvaconf


class BaseGroup(SilvaObject, SimpleItem):

    implements(interfaces.IBaseGroup)

    security = ClassSecurityInfo()

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
    ) + SimpleItem.manage_options

    silvaconf.baseclass()

    def __init__(self, id, group_name):
        BaseGroup.inheritedAttribute('__init__')(self, id)
        self._group_name = group_name

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'isValid')
    def isValid(self):
        """Returns whether the group asset is valid.
        """
        return (self.valid_path == self.getPhysicalPath())

InitializeClass(BaseGroup)

class Group(BaseGroup):
    """Silva Group"""

    meta_type = "Silva Group"
    security = ClassSecurityInfo()

    implements(interfaces.IGroup)

    manage_main = PageTemplateFile('www/groupEdit', globals())

    silvaconf.icon('www/group.png')
    silvaconf.factory('manage_addGroup')

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

def manage_addGroupUsingFactory(factory, context, id, title,
                                group_name, asset_only=0, REQUEST=None):
    """Add a Group using factory."""
    if not asset_only:
        if not mangle.Id(context, id).isValid():
            return
        # these checks should also be repeated in the UI
        if not hasattr(context, 'service_groups'):
            raise AttributeError, "There is no service_groups"
        if context.service_groups.isGroup(group_name):
            raise ValueError, "There is already a group of that name."
    object = factory(id, group_name)
    context._setObject(id, object)
    object = getattr(context, id)
    object.set_title(title)
    # set the valid_path, this cannot be done in the constructor
    # because the context is not known as the object is not inserted
    # into the container.
    object.valid_path = object.getPhysicalPath()
    if not asset_only:
        addGroupToService(context.service_groups, object)
    add_and_edit(context, id, REQUEST)
    return ''


def manage_addGroup(*args, **kwargs):
    """Add a Group.
    """
    return manage_addGroupUsingFactory(Group, *args, **kwargs)

@silvaconf.subscribe(
    interfaces.IBaseGroup, OFS.interfaces.IObjectWillBeRemovedEvent)
def group_will_be_removed(group, event):
    """Unregister group when it's deleted.
    """
    if group.isValid() and hasattr(group, 'service_groups'):
        removeGroupFromService(group.service_groups, group)

def addGroupToService(service, group):
    """Register a group with the correct method.
    """

    if interfaces.IGroup.providedBy(group):
        service.addNormalGroup(group._group_name)
    elif interfaces.IIPGroup.providedBy(group):
        service.addIPGroup(group._group_name)
    elif interfaces.IVirtualGroup.providedBy(group):
        service.addVirtualGroup(group._group_name)
    else:
        raise ValueError, 'Unknown group while adding to the service'

def removeGroupFromService(service, group):
    """Remove a group with the correct method.
    """

    if interfaces.IGroup.providedBy(group):
        service.removeNormalGroup(group._group_name)
    elif interfaces.IIPGroup.providedBy(group):
        service.removeIPGroup(group._group_name)
    elif interfaces.IVirtualGroup.providedBy(group):
        service.removeVirtualGroup(group._group_name)
    else:
        raise ValueError, 'Unknown group while removing it from the service'

