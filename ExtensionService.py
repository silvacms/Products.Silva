
# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.19 $
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
                
    # ACCESSORS

    security.declareProtected('View management screens', 'get_names')
    def get_names(self):
        """Return registered extension names
        """
        return extensionRegistry.get_names()

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

manage_addExtensionServiceForm = PageTemplateFile(
    "www/extensionServiceAdd", globals(), __name__='manage_addExtensionServiceForm')

def manage_addExtensionService(self, id, title='', REQUEST=None):
    """Add extension service."""
    object = ExtensionService(id, title)    
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
