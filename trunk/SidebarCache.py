# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class SidebarCache(SimpleItem):
    """The actual storage of the cache"""

    meta_type = 'Silva Sidebar Cache'
    security = ClassSecurityInfo()
    
    def __init__(self, id):
        self.id = id
        self._sidebar_cache = OOBTree()
        self._path_mapping = OOBTree()

InitializeClass(SidebarCache)

def manage_addSidebarCache(self, id, REQUEST=None):
    """Add the sidebar cache to a folder (will usually be temp storage)"""
    id = self._setObject(id, SidebarCache(id))
    return ''
