# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
from zope.interface import implements

from AccessControl import ClassSecurityInfo, Unauthorized
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
import SilvaPermissions

from Group import BaseGroup, manage_addGroupUsingFactory
from silva.core import interfaces
from silva.core import conf as silvaconf

class VirtualGroup(BaseGroup):
    """Silva Virtual Group"""

    meta_type = "Silva Virtual Group"    
    security = ClassSecurityInfo()
    
    implements(interfaces.IVirtualGroup)

    manage_main = PageTemplateFile('www/virtualGroupEdit', globals())

    silvaconf.icon('www/virtual_group.png')
    silvaconf.factory('manage_addVirtualGroup')
    
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

def manage_addVirtualGroup(*args, **kwargs):
    """Add a Virtual Group."""
    return manage_addGroupUsingFactory(VirtualGroup, *args, **kwargs)


