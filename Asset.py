# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.17 $
# Zope
from zope.interface import implements

from Globals import InitializeClass
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware

# Silva
from SilvaObject import SilvaObject
import SilvaPermissions

from interfaces import IAsset

class Asset(CatalogPathAware, SilvaObject, SimpleItem.SimpleItem):
    implements(IAsset)

    security = ClassSecurityInfo()

    default_catalog = 'service_catalog'

    object_type = 'asset'

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_title')
    def set_title(self, title):
        """Set the title of the silva object.
        """
        # FIXME: Ugh. I get unicode from formulator but this will not validate
        # when using the metadata system. So first make it into utf-8 again..
        title = title.encode('utf-8')
        binding = self.service_metadata.getMetadata(self)
        binding.setValues(
            'silva-content', {'maintitle': title}, reindex=1)
        self.reindex_object()
        
    def manage_afterAdd(self, item, container):
        self._afterAdd_helper(item, container)
        self._set_creation_datetime()
        Asset.inheritedAttribute('manage_afterAdd')(self, item, container)
        
    def manage_beforeDelete(self, item, container):
        self._beforeDelete_helper(item, container)
        Asset.inheritedAttribute('manage_beforeDelete')(self, item, container)

    def is_deletable(self):
        """assets are deletable

            NOTE: once there is reference management those should only be
            deletable if not referenced
        """
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_navigation_links')
    def get_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.
        
        This can be used by Mozilla in the accessibility toolbar.
        """
        return {}

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'version_status')
    def version_status(self):
        return 'public'

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                            'fulltext')
    def fulltext(self):
        fulltextlist = [self.id, self.get_title()]
        return fulltextlist
    
InitializeClass(Asset)
