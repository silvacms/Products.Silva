# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# silva imports
from zope.interface import implements
from Products.Silva import upgrade
from Products.Silva.interfaces import IUpgrader, ISilvaObject, IRoot
import zLOG

def initialize():
    ## taking this upgrader out, until we can fix sec_clean_roles to
    ## get around the get_valid_userids OverFlowError issue.
    ## upgrade.registry.registerUpgrader(
    ##     CleanRolesUpgrader(), '2.1', upgrade.AnyMetaType)
    upgrade.registry.registerUpgrader(
        AutoTOCUpgrader(), '2.1', 'Silva AutoTOC')

class AutoTOCUpgrader:

    implements(IUpgrader)

    def upgrade(self, autotoc):
        zLOG.LOG(
            'Silva', zLOG.INFO,
            'Upgrading AutoTOC: %s' % autotoc.get_title_or_id())
        if not hasattr(autotoc,'_local_types'):
            autotoc._local_types = ['Silva Document', 'Silva Publication',
                                 'Silva Folder']
        if not hasattr(autotoc, '_toc_depth'):
            autotoc._toc_depth = -1
        if not hasattr(autotoc, '_display_desc_flag'):
            autotoc._display_desc_flag = False
        if not hasattr(autotoc, '_sort_order'):
            autotoc._sort_order = "silva"
        if not hasattr(autotoc, '_show_icon'):
            autotoc._show_icon = False
        autotoc.index_object()
        return autotoc

## class CleanRolesUpgrader:
##     """Calls sec_clean_roles on each ISilvaObject to remove any stale
##        username->rolemappings (bug #100561)"""
##     implements(IUpgrader)

##     def upgrade(self, obj):
##         if IRoot.providedBy(obj):
##             zLOG.LOG('Silva', zLOG.INFO, "Cleaning Stale Role Mappings: this may take some time")
##         if ISilvaObject.providedBy(obj):
##             obj.sec_clean_roles()
##         return obj
