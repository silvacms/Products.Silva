# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
# Silva
from helpers import add_and_edit
import SilvaPermissions
from ExtensionRegistry import extensionRegistry


class ExtensionService(SimpleItem.SimpleItem):
    meta_type = 'Silva Extension Service'

    security = ClassSecurityInfo()
    
    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/extensionServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    def __init__(self, id, title):
        self.id = id
        self.title = title

    # MANIPULATORS

    security.declareProtected('View management screens', 'install')
    def install(self, name):
        """Install extension
        """
        root = self.aq_inner.aq_parent
        extensionRegistry.install(name, root)
        root.service_view_registry.set_trees(self.get_installed_names())
        return self.manage_main(manage_tabs_message='%s installed' % name)

    security.declareProtected('View management screens', 'uninstall')
    def uninstall(self, name):
        """Uninstall extension
        """
        root = self.aq_inner.aq_parent
        extensionRegistry.uninstall(name, root)
        root.service_view_registry.set_trees(self.get_installed_names())
        return self.manage_main(manage_tabs_message='%s uninstalled' % name)
        
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
