# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: VirtualGroup.py,v 1.1 2003/01/20 11:24:29 zagy Exp $
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
        self.service_groups.removeVirtualGroup(self._group_name)


    # MANIPULATORS
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'addGroup')
    def addGroup(self, group):
        self.service_groups.addGroupToVirtualGroup(group, self._group_name)
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'removeGroup')
    def removeGroup(self, group):
        self.service_groups.removeGroupFromVirtualGroup(
            group, self._group_name)
    
    # ACCESSORS    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'listGroups')
    def listGroups(self):
        result = self.service_groups.listGroupsInVirtualGroup(self._group_name)
        result.sort()
        return result

InitializeClass(VirtualGroup)

manage_addVirtualGroupForm = PageTemplateFile(
    "www/virtualGroupAdd", globals(),
    __name__='manage_addVirtualGroupForm')

def manage_addVirtualGroup(self, id, title, group_name, REQUEST=None):
    """Add a Virtual Group."""
    if not self.is_id_valid(id):
        return
    if not hasattr(self, 'service_groups'):
        return  
    if self.service_groups.isGroup(group_name):
        return
    object = VirtualGroup(id, title, group_name)
    self._setObject(id, object)
    object = getattr(self, id)
    self.service_groups.addVirtualGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''
