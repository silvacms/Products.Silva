# zope imports
import zLOG
# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade, upgrade_110

# There's not real upgrade from 1.3 to 1.4 however, we still register
# a dummy upgrader to keep the upgrader version registry coherent.

def initialize():
    upgrade.registry.registerUpgrader(
        upgrade_110.DummyUpgrader(), '1.4', 'Silva Root')
