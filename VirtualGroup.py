# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: VirtualGroup.py,v 1.18 2006/01/24 16:14:13 faassen Exp $
from zope.interface import implements

from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from OFS.SimpleItem import SimpleItem
# Silva
from SilvaObject import SilvaObject
import SilvaPermissions
from Products.Silva import mangle
# misc
from helpers import add_and_edit

from interfaces import ISilvaObject

class VirtualGroup(SilvaObject, SimpleItem):
    """Silva Virtual Group"""
    security = ClassSecurityInfo()

    meta_type = "Silva Virtual Group"
    
    implements(ISilvaObject)

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
    ) + SimpleItem.manage_options

    manage_main = PageTemplateFile('www/virtualGroupEdit', globals())

    def __init__(self, id, title, group_name):
        VirtualGroup.inheritedAttribute('__init__')(self, id)
        self._group_name = group_name

    def manage_beforeDelete(self, item, container):
        VirtualGroup.inheritedAttribute('manage_beforeDelete')(self, item, container)
        if self.isValid():
            self.service_groups.removeVirtualGroup(self._group_name)

    def isValid(self):
        """returns whether the group asset is valid

            A group asset becomes invalid if it gets moved around ...
        """
        return (self.valid_path == self.getPhysicalPath())
    
    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Get the title of this group.
        """
        return self._title

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    get_short_title = get_title

    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'addGroup')
    def addGroup(self, group):
        """add a group to the virtual group"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        
        self.service_groups.addGroupToVirtualGroup(group, self._group_name)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'copyGroupsFromVirtualGroups')
    def copyGroupsFromVirtualGroups(self, virtual_groups):
        sg = self.service_groups
        groups = {}
        for virtual_group in virtual_groups:        
            if sg.isVirtualGroup(virtual_group):
                for group in sg.listGroupsInVirtualGroup(virtual_group):
                    groups[group] = 1
        current_groups = self.listGroups()
        groupids = [groupid for groupid in groups.keys() 
                    if groupid not in current_groups]
        for groupid in groupids:
            self.addGroup(groupid)
        # For UI feedback
        return groupids

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'removeGroup')
    def removeGroup(self, group):
        """removes a group from the vgroup"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        self.service_groups.removeGroupFromVirtualGroup(
            group, self._group_name)
    
    # ACCESSORS    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'listGroups')
    def listGroups(self):
        """list groups in this vgroup"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        result = self.service_groups.listGroupsInVirtualGroup(self._group_name)
        result.sort()
        return result

InitializeClass(VirtualGroup)

def manage_addVirtualGroup(self, id, title, group_name, asset_only=0,
        REQUEST=None):
    """Add a Virtual Group."""
    if not asset_only:
        if not mangle.Id(self, id).isValid():
            return
        if not hasattr(self, 'service_groups'):
            raise AttributeError, "There is no service_groups"
        if self.service_groups.isGroup(group_name):
            raise ValueError, "There is already a group of that name."
    object = VirtualGroup(id, title, group_name)
    self._setObject(id, object)
    object = getattr(self, id)
    # set the valid_path, this cannot be done in the constructor because the context
    # is not known as the object is not inserted into the container.
    object.valid_path = object.getPhysicalPath()
    if not asset_only:
        self.service_groups.addVirtualGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''
