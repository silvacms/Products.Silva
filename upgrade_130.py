# zope imports
import zLOG
# silva imports
from Products.Silva.interfaces import IUpgrader
from Products.Silva import upgrade, upgrade_100

def initialize():
    upgrade.registry.registerUpgrader(
        upgrade_100.RefreshAll(), '1.3', 'Silva Root')
