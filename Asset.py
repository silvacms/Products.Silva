# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.9 $
# Zope
from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware

# Silva
from SilvaObject import SilvaObject
import SilvaPermissions

from interfaces import IAsset

class Asset(SilvaObject, SimpleItem.SimpleItem, CatalogPathAware):
    __implements__ = IAsset

    security = ClassSecurityInfo()

    default_catalog = 'service_catalog'

    object_type = 'asset'

    def manage_afterAdd(self, item, container):
        Asset.inheritedAttribute('manage_afterAdd')(self, item, container)
        self.index_object()
        
    def manage_beforeDelete(self, item, container):
        Asset.inheritedAttribute('manage_beforeDelete')(self, item, container)
        self.unindex_object()
        
    def manage_afterClone(self, item):
        Asset.inheritedAttribute('manage_afterClone')(self, item)
        self.index_object()
        
InitializeClass(Asset)
