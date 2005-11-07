# zope imports
import zLOG
# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade

class DummyUpgrader:

    __implements__ = IUpgrader
    
    def upgrade(self, silvaroot):
        return silvaroot
    
# There's not real upgrade from 1.0 to 1.1 however, we still register
# a dummy upgrader to keep the upgrader version registry coherent.

def initialize():
    upgrade.registry.registerUpgrader(DummyUpgrader(), '1.1', 'Silva Root')
