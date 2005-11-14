from zope.interface import implements

# zope imports
import zLOG

# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade

#-----------------------------------------------------------------------------
# 1.1 to 1.2
#-----------------------------------------------------------------------------

class CatalogUpgrade:
    """Call the setup_catalog method in the install module - this will
    make sure the catalog is there and has all of the necessary indeces, 
    without removing anything.
    """

    implements(IUpgrader)

    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Make sure the Catalog's indeces are up to date") 
        from Products.Silva import install
        install.setup_catalog(silvaroot)
        return silvaroot
    
class ReindexHauntedPath:
    """After the Catalog's indeces are updated, reindex the hauted_path
    index. This is to make sure existing Ghosts will work with the
    subscriptions feature - This reindexing is an expensive operation!
    """
    
    implements(IUpgrader)
    
    def upgrade(self, silvaroot):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            "Reindex the hauted_path index - may take a while")
        catalog = silvaroot.service_catalog
        catalog.reindexIndex('haunted_path', None)
        return silvaroot

class UpdateIndexers:
    """The indexers' implementation has changed. We need to trigger
    an update call on each instance to get the contained information
    up to date.
    """
    
    implements(IUpgrader)
    
    def upgrade(self, indexer):
        zLOG.LOG(
            'Silva', zLOG.INFO, 
            'Update index for %s' % '/'.join(indexer.getPhysicalPath()))
        indexer.update()
        return indexer
    
class RefreshAll:
    " refresh all products "

    implements(IUpgrader)

    def upgrade(self, root):
        zLOG.LOG('Silva', zLOG.INFO, 'refresh all installed products') 
        root.service_extensions.refresh_all()
        return root
    
def initialize():
    upgrade.registry.registerUpgrader(CatalogUpgrade(), '1.2', 'Silva Root')
    upgrade.registry.registerUpgrader(ReindexHauntedPath(), '1.2', 'Silva Root')
    upgrade.registry.registerUpgrader(UpdateIndexers(), '1.2', 'Silva Indexer')
    upgrade.registry.registerUpgrader(RefreshAll(), '1.2', 'Silva Root')
