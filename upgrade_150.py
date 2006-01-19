# silva imports
import zLOG
from zope.interface import implements
from Products.Silva import upgrade, upgrade_100
from Products.Silva.interfaces import IUpgrader
from zExceptions import BadRequest

def initialize():
    upgrade.registry.registerUpgrader(PlacelessTranslationServiceDestroy(),
                                      '1.5', 'Silva Root')
    upgrade.registry.registerUpgrader(RemoveServiceLayout(), '1.5',
                                      'Silva Root')
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
                'Silva', zLOG.INFO,
                'service_layouts is already gone')

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
                "PlacelessTranslationService is already gone")
        return silvaroot

