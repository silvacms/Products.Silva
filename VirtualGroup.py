# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: VirtualGroup.py,v 1.3 2003/01/24 08:45:55 zagy Exp $
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

class VirtualGroup(Asset):
    security = ClassSecurityInfo()

    meta_type = "Silva Virtual Group"
    
    __implements__ = IAsset

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
    ) + Asset.manage_options

    manage_main = PageTemplateFile('www/virtualGroupEdit', globals())

    def __init__(self, id, title, group_name):
        VirtualGroup.inheritedAttribute('__init__')(self, id, title)
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

    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'addGroup')
    def addGroup(self, group):
        """add a group to the virtual group"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        
        self.service_groups.addGroupToVirtualGroup(group, self._group_name)
        
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

manage_addVirtualGroupForm = PageTemplateFile(
    "www/virtualGroupAdd", globals(),
    __name__='manage_addVirtualGroupForm')

def manage_addVirtualGroup(self, id, title, group_name, asset_only=0,
        REQUEST=None):
    """Add a Virtual Group."""
    if not asset_only:
        if not self.is_id_valid(id):
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
