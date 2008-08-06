# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# silva imports
from Products.Silva.upgrade import BaseUpgrader, BaseRefreshAll

import zLOG

#-----------------------------------------------------------------------------
# 1.1.0 to 1.2.0
#-----------------------------------------------------------------------------

VERSION='1.2'

class CatalogUpgrade(BaseUpgrader):
    """Call the setup_catalog method in the install module - this will
    make sure the catalog is there and has all of the necessary indeces, 
    without removing anything.
    """

    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Make sure the Catalog's indeces are up to date") 
        from Products.Silva import install
        install.setup_catalog(silvaroot)
        return silvaroot

catalogUpgrade = CatalogUpgrade(VERSION, 'Silva Root', 10)

    
class ReindexHauntedPath(BaseUpgrader):
    """After the Catalog's indeces are updated, reindex the hauted_path
    index. This is to make sure existing Ghosts will work with the
    subscriptions feature - This reindexing is an expensive operation!
    """
    
    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Reindex the hauted_path index - may take a while")
        catalog = silvaroot.service_catalog
        catalog.reindexIndex('haunted_path', None)
        return silvaroot

reindexHauntedPath = ReindexHauntedPath(VERSION, 'Silva Root', 20)

class UpdateIndexers(BaseUpgrader):
    """The indexers' implementation has changed. We need to trigger
    an update call on each instance to get the contained information
    up to date.
    """
    
    def upgrade(self, indexer):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            'Update index for %s' % '/'.join(indexer.getPhysicalPath()))
        indexer.update()
        return indexer

updateIndexers = UpdateIndexers(VERSION, 'Silva Indexer')

class RefreshAll(BaseRefreshAll):
    pass

refreshAll = RefreshAll(VERSION, 'Silva Root', 30)




