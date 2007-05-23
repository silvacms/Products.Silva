# silva imports
from Products.Silva import upgrade, upgrade_100

def initialize():
    upgrade.registry.registerUpgrader(
        upgrade_100.RefreshAll(), '2.0', 'Silva Root')
