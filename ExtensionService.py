
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.21 $
# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime
# Silva
from helpers import add_and_edit
import SilvaPermissions
from ExtensionRegistry import extensionRegistry
from Products.Silva.interfaces import ISilvaObject, IVersion, IContainer, IAsset
import install

class ExtensionService(SimpleItem.SimpleItem):
    meta_type = 'Silva Extension Service'

    security = ClassSecurityInfo()
    
    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        {'label':'Partial upgrades', 'action':'manage_partialUpgradeForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/extensionServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 
                                'manage_partialUpgradeForm')
    manage_partialUpgradeForm = PageTemplateFile(
                    'www/extensionServicePartialUpgrades', globals(),  
                    __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    _quota_enabled = False

    def __init__(self, id, title):
        self.id = id
        self.title = title
        # Actually is the cache refresh datetime
        self._refresh_datetime = DateTime()
        
    # MANIPULATORS

    security.declareProtected('View management screens', 'install')
    def install(self, name, REQUEST=None):
        """Install extension
        """
        root = self.aq_inner.aq_parent
        extensionRegistry.install(name, root)
        productsWithView = [
            inst_name for inst_name in self.get_installed_names() 
            if inst_name in root.service_views.objectIds()]
        root.service_view_registry.set_trees(productsWithView)
        if REQUEST:
            return self.manage_main(manage_tabs_message='%s installed' % name)

    security.declareProtected('View management screens', 'uninstall')
    def uninstall(self, name, REQUEST=None):
        """Uninstall extension
        """
        root = self.aq_inner.aq_parent
        extensionRegistry.uninstall(name, root)
        productsWithView = [
            inst_name for inst_name in self.get_installed_names() 
            if inst_name in root.service_views.objectIds()]
        root.service_view_registry.set_trees(productsWithView)
        if REQUEST:
            return self.manage_main(manage_tabs_message='%s uninstalled' % name)

    security.declareProtected('View management screens', 'refresh')
    def refresh(self, name, REQUEST=None):
        """Refresh (uninstall/install) extension.
        """
        self.uninstall(name)
        self.install(name)
        self.refresh_caches()
        if REQUEST:
            return self.manage_main(manage_tabs_message='%s refreshed' % name)

    security.declareProtected('View management screens', 'refresh_all')
    def refresh_all(self, REQUEST=None):
        """Refreshes all extensions
        """
        for name in self.get_installed_names():
            self.refresh(name)
        if REQUEST:
            return self.manage_main(manage_tabs_message=
                'Silva and all installed extensions have been refreshed')
                
    security.declareProtected('View management screens', 'refresh_caches')
    def refresh_caches(self):        
        """Refresh caches
        """
        self._refresh_datetime = DateTime()

    security.declareProtected('View management screens', 'upgrade_all')
    def upgrade_all(self):
        """Upgrades all content
        """
        self.get_root().upgrade_silva()
        return self.manage_main(manage_tabs_message=
            "Content upgrade succeeded. See event log for details.")

    security.declareProtected('View management screens', 'upgrade_object')
    def upgrade_object(self, REQUEST):
        """Upgrades a single object (recursively)

            Experimental!!
        """
        if not REQUEST.has_key('version') or not REQUEST.has_key('path'):
            return self.manage_partialUpgradeForm(manage_tabs_message=
                "Content upgrade failed: missing arguments")
        path = REQUEST['path']
        version = REQUEST['version']
        self.get_root().upgrade_silva_object(version, path)
        return self.manage_partialUpgradeForm(manage_tabs_message=
            "Content upgrade succeeded. See event log for details.")

    security.declareProtected('View management screens', 'install_layout')
    def install_layout(self):
        """Install core layout.
        """
        root = self.aq_inner.aq_parent
        install.configureLayout(root, 1)
        return self.manage_main(manage_tabs_message = 	 
                                'Default layout code installed')

    security.declareProtected('View management screens',
                              'refresh_catalog')
    def refresh_catalog(self):
        """Refresh the silva catalog.
        """
        root = self.aq_inner.aq_parent
        root.service_catalog.manage_catalogClear()
        self._reindex(root)
        return self.manage_main(manage_tabs_message = 	 
                                'Catalog refreshed.')

    def _reindex(self, obj):
        """Reindex a silva object or version.
        """
        if ISilvaObject.providedBy(obj) and getattr(obj, 'index_object', None):
            obj.index_object()
        elif IVersion.providedBy(obj) and getattr(obj, 'index_object', None):
            if obj.version_status() != 'last_closed' and obj.version_status(
                ) != 'closed' :
                obj.index_object()
        for child in obj.objectValues():
            self._reindex(child)

    security.declareProtected('View management screens',
                              'disable_quota_subsystem')
    def disable_quota_subsystem(self, REQUEST=None):
        """Disable quota sub-system.
        """
        assert (self._quota_enabled)

        self._quota_enabled = False
        if REQUEST:
            return self.manage_main(manage_tabs_message = 	 
                                    'Quota sub-system disabled.')

    security.declareProtected('View management screens',
                              'enable_quota_subsystem')
    def enable_quota_subsystem(self, REQUEST=None):
        """Enable quota sub-system.
        """
        assert (not self._quota_enabled)

        def visitor(item):
            total = 0
            if IContainer.providedBy(item):
                used_space = 0
                for _, obj in item.objectItems():
                    used_space += visitor(obj)
                item.used_space = used_space
                total += used_space
            elif IAsset.providedBy(item):
                total += item.reset_quota()
            return total

        root = self.get_root()
        root.used_space = visitor(root)
        self._quota_enabled = True
        if REQUEST:
            return self.manage_main(manage_tabs_message = 	 
                                    'Quota sub-system enabled.')

        
    # ACCESSORS

    security.declareProtected('Access contents information',
                              'get_quota_subsystem_status')
    def get_quota_subsystem_status(self):
        return self._quota_enabled

    security.declareProtected('View management screens', 'get_names')
    def get_names(self):
        """Return registered extension names
        """
        return extensionRegistry.get_names()

    security.declareProtected('View management screens', 'get_version_info')
    def get_version_info(self, name):
        mname = extensionRegistry.get_product_module_name(name)
        product_info = self.unrestrictedTraverse('/Control_Panel/Products/' + mname)
        return product_info.version
        
    def get_installed_names(self):
        """Return installed extension names
        """
        return [name for name in self.get_names()
                if self.is_installed(name)]

    security.declareProtected('View management screens', 'get_description')
    def get_description(self, name):
        """Return description of extension
        """
        return extensionRegistry.get_description(name)

    security.declareProtected('View management screens', 'get_depends_on')
    def get_depends_on(self, name):
        """Return extension dependency
        """
        return extensionRegistry.get_depends_on(name)

    security.declareProtected('View management screens', 'is_installed')
    def is_installed(self, name):
        """Is extension installed?
        """
        root = self.aq_inner.aq_parent
        return extensionRegistry.is_installed(name, root)

    security.declareProtected('View management screens',
                              'get_refresh_datetime')
    def get_refresh_datetime(self):
        """Get datetime of last refresh.
        """
        return self._refresh_datetime
    
InitializeClass(ExtensionService)

def manage_addExtensionService(self, id, title='', REQUEST=None):
    """Add extension service."""
    object = ExtensionService(id, title)    
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
