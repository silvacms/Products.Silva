# Copyright (c) 2003-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: IPGroup.py,v 1.9 2006/01/25 18:13:30 faassen Exp $
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

from interfaces import IIPGroup

class IPGroup(SilvaObject, SimpleItem):
    """Silva IP Group"""
    security = ClassSecurityInfo()

    meta_type = "Silva IP Group"
    
    implements(IIPGroup)

    def __init__(self, id, title, group_name):
        IPGroup.inheritedAttribute('__init__')(self, id, title)
        self._group_name = group_name


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
        SilvaPermissions.ChangeSilvaAccess, 'addIPRange')
    def addIPRange(self, iprange):
        """add a group to the ip group"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        gs = self.service_groups
        iprange = gs.createIPRange(iprange)
        gs.addIPRangeToIPGroup(iprange, self._group_name)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'copyIPRangesFromIPGroups')
    def copyIPRangesFromIPGroups(self, ipgroups):
        """copy ip ranges from ip groups"""
        sg = self.service_groups
        ipranges = {}
        for ipgroup in ipgroups:
            if sg.isIPGroup(ipgroup):
                for iprange in sg.listIPRangesInIPGroup(ipgroup):
                    ipranges[iprange] = 1
        have_ranges = self.listIPRanges()
        add_ranges = [ iprange
            for iprange in ipranges.keys()
            if iprange not in have_ranges]
        for iprange in add_ranges:
            sg.addIPRangeToIPGroup(iprange, self._group_name)
        return add_ranges

    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'removeIPRange')
    def removeIPRange(self, iprange):
        """removes a group from the vgroup"""
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        gs = self.service_groups
        iprange = gs.createIPRange(iprange)
        gs.removeIPRangeFromIPGroup(iprange, self._group_name)
    
    # ACCESSORS    
    security.declareProtected(
        SilvaPermissions.ChangeSilvaAccess, 'listIPRanges')
    def listIPRanges(self):
        """list ip ranges in ipgroups """
        if not self.isValid():
            raise Unauthorized, "Zombie group asset"
        result = self.service_groups.listIPRangesInIPGroup(self._group_name)
        result.sort()
        return result

InitializeClass(IPGroup)

def ipgroup_will_be_removed(ipgroup, event):
    if ipgroup.isValid():
        ipgroup.service_groups.removeIPGroup(ipgroup._group_name)

def manage_addIPGroup(self, id, title, group_name, asset_only=0,
        REQUEST=None):
    """Add a IP Group."""
    if not asset_only:
        if not mangle.Id(self, id).isValid():
            return
        if not hasattr(self, 'service_groups'):
            raise AttributeError, "There is no service_groups"
        if self.service_groups.isGroup(group_name):
            raise ValueError, "There is already a group of that name."
    object = IPGroup(id, title, group_name)
    self._setObject(id, object)
    object = getattr(self, id)
    # set the valid_path, this cannot be done in the constructor because the 
    # context is not known as the object is not inserted into the container.
    object.valid_path = object.getPhysicalPath()
    if not asset_only:
        self.service_groups.addIPGroup(group_name)
    add_and_edit(self, id, REQUEST)
    return ''
