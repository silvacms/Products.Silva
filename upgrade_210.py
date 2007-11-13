# silva imports
from zope.interface import implements
from Products.Silva import upgrade
from Products.Silva.interfaces import IUpgrader, ISilvaObject, IRoot
import zLOG

def initialize():
    upgrade.registry.registerUpgrader(
        CleanRolesUpgrader(), '2.1', upgrade.AnyMetaType)

class CleanRolesUpgrader:
    """Calls sec_clean_roles on each ISilvaObject to remove any stale
       username->rolemappings (bug #100561)"""
    implements(IUpgrader)

    def upgrade(self, obj):
        if IRoot.providedBy(obj):
            zLOG.LOG('Silva', zLOG.INFO, "Cleaning Stale Role Mappings: this may take some time")
        if ISilvaObject.providedBy(obj):
            obj.sec_clean_roles()
        return obj
