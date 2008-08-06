# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# silva imports
import zLOG
from zExceptions import BadRequest
from BTrees.Length import Length
from Products.Silva.upgrade import BaseUpgrader, BaseRefreshAll

#-----------------------------------------------------------------------------
# 1.4.0 to 1.5.0
#-----------------------------------------------------------------------------

VERSION='1.5'

class RefreshAll(BaseRefreshAll):
    pass

refreshAll = RefreshAll(VERSION, 'Silva Root', 40)
    
class RemoveServiceLayout(BaseUpgrader):
    """Remove old-style never quite released ServiceLayout.
    """

    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Removing service_layouts")
        try:
            silvaroot.manage_delObjects(['service_layouts'])
        except BadRequest:
            zLOG.LOG(
                'Silva', zLOG.INFO, 'service_layouts is already gone')

        return silvaroot

removeServiceLayout = RemoveServiceLayout(VERSION, 'Silva Root', 30)

class PlacelessTranslationServiceDestroy(BaseUpgrader):
    """Destroy traces of PTS in Zope.
    """

    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO,
            'Destroying remains of PlacelessTranslationService')
        # nasty to get to Zope root, but we want PTS eliminated
        cp = silvaroot.Control_Panel
        try:
            cp._delObject('TranslationService')
        except AttributeError:
            zLOG.LOG(
                'Silva', zLOG.INFO,
                'PlacelessTranslationService is already gone')
        return silvaroot

placelessTranslationServiceDestroy = PlacelessTranslationServiceDestroy(VERSION, 'Silva Root', 20)

class IndexUpgrader(BaseUpgrader):
    """Actually this should be in Zope itself, as it fixes a Zope 
       core issue.

       In Zope 2.8.x there was an internal API change in the UnIndex class,
       a superclass of some ZCatalog Indexes and in the PathIndex (which
       very much looks like an UnIndex class, but does not derive from it).
       
       For this change (they added an attribute called '_length' to the
       code) no upgrader was provided in Zope itself, however.
       
       This upgrader tries to solve this problem.
       """

    def __init__(self, version, meta_type, catalog_id='service_catalog'):
        super(IndexUpgrader, self).__init__(version, meta_type)
        self._catalog_id = catalog_id
    
    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            'Upgrading ZCatalog Indexes of %s' % self._catalog_id)
        catalog = getattr(silvaroot, self._catalog_id)
        for index in catalog.index_objects():
            self._migrate_length(index)
        return silvaroot
        
    def _migrate_length(self, obj):
        if not hasattr(obj, '_unindex'):
            return obj
        if hasattr(obj, '_length'):
            zLOG.LOG(
                'Silva', zLOG.INFO,
                'Skipping already upgraded index %s' % obj.id)
            return obj
        zLOG.LOG(
            'Silva', zLOG.INFO, 'Upgrading index %s' % obj.id)
        obj._length = Length(len(obj._unindex))
        return obj

indexUpgrader = IndexUpgrader(VERSION, 'Silva Root')
