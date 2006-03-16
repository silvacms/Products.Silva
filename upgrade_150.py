# silva imports
import zLOG
from zope.interface import implements
from zExceptions import BadRequest
from BTrees.Length import Length
from Products.Silva import upgrade, upgrade_100
from Products.Silva.interfaces import IUpgrader

def initialize():
    upgrade.registry.registerUpgrader(
        IndexUpgrader(), '1.5', 'Silva Root')
    upgrade.registry.registerUpgrader(
        PlacelessTranslationServiceDestroy(), '1.5', 'Silva Root')
    upgrade.registry.registerUpgrader(
        RemoveServiceLayout(), '1.5', 'Silva Root')
    upgrade.registry.registerUpgrader(
        upgrade_100.RefreshAll(), '1.5', 'Silva Root')
    
class RemoveServiceLayout:
    """Remove old-style never quite released ServiceLayout.
    """

    implements(IUpgrader)

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

class PlacelessTranslationServiceDestroy:
    """Destroy traces of PTS in Zope.
    """

    implements(IUpgrader)

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

class IndexUpgrader:
    """Actually this should be in Zope itself, as it fixes a Zope 
       core issue.

       In Zope 2.8.x there was an internal API change in the UnIndex class,
       a superclass of some ZCatalog Indexes and in the PathIndex (which
       very much looks like an UnIndex class, but does not derive from it).
       
       For this change (they added an attribute called '_length' to the
       code) no upgrader was provided in Zope itself, however.
       
       This upgrader tries to solve this problem.
       """

    implements(IUpgrader)
    
    def __init__(self, catalog_id='service_catalog'):
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
        if not hasattr(obj, '_unindex'):
            print repr(obj)
        zLOG.LOG(
            'Silva', zLOG.INFO, 'Upgrading index %s' % obj.id)
        obj._length = Length(len(obj._unindex))
        return obj
