# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.8.12.1 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware

# Silva interfaces
from IAsset import IAsset
# Silva
from SilvaObject import SilvaObject
import SilvaPermissions

class Asset(CatalogPathAware, SilvaObject, SimpleItem.SimpleItem):
    __implements__ = IAsset

    security = ClassSecurityInfo()

    default_catalog = 'service_catalog'

    object_type = 'asset'

    def manage_afterAdd(self, item, container):
        self._afterAdd_helper(item, container)
        Asset.inheritedAttribute('manage_afterAdd')(self, item, container)
        
    def manage_beforeDelete(self, item, container):
        self._beforeDelete_helper(item, container)
        Asset.inheritedAttribute('manage_beforeDelete')(self, item, container)
        
    def manage_afterClone(self, item):
        Asset.inheritedAttribute('manage_afterClone')(self, item)
        
InitializeClass(Asset)
