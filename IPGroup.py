# Copyright (c) 2003-2009 Infrae. All rights reserved.
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

class IPGroup(BaseGroup):
    """Silva IP Group"""

    meta_type = "Silva IP Group"    
    security = ClassSecurityInfo()
    
    implements(interfaces.IIPGroup)

    manage_main = PageTemplateFile('www/ipGroupEdit', globals())

    silvaconf.icon('www/ip_group.png')
    silvaconf.factory('manage_addIPGroup')
    
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

def manage_addIPGroup(*args, **kwargs):
    """Add a IP Group.
    """
    return manage_addGroupUsingFactory(IPGroup, *args, **kwargs)
