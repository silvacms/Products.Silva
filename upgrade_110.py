# silva imports
from Products.Silva import upgrade, upgrade_100

def initialize():
    upgrade.registry.registerUpgrader(
        upgrade_100.RefreshAll(), '1.1', 'Silva Root')
