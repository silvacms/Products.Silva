# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.12.32.1.16.1 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware

# Silva
from SilvaObject import SilvaObject
import SilvaPermissions

from interfaces import IAsset

class Asset(CatalogPathAware, SilvaObject, SimpleItem.SimpleItem):
    __implements__ = IAsset

    security = ClassSecurityInfo()

    default_catalog = 'service_catalog'

    object_type = 'asset'

    def manage_afterAdd(self, item, container):
        self._afterAdd_helper(item, container)
        self._set_creation_datetime()
        Asset.inheritedAttribute('manage_afterAdd')(self, item, container)
        
    def manage_beforeDelete(self, item, container):
        self._beforeDelete_helper(item, container)
        Asset.inheritedAttribute('manage_beforeDelete')(self, item, container)

    def is_deletable(self):
        """assets are delteable

            NOTE: once there is reference management those should only be
            deletable if not referenced
        """
        return 1

InitializeClass(Asset)
