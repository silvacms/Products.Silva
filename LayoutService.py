# Copyright (c) 2003-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.18 $

# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from DateTime import DateTime
# Silva
from helpers import add_and_edit
import SilvaPermissions
from LayoutRegistry import layoutRegistry, DEFAULT_LAYOUT
import LayoutRegistry
import install
import random
import copy

class LayoutService(SimpleItem.SimpleItem):
    meta_type = 'Silva Layout Service'

    security = ClassSecurityInfo()
    
    manage_options = (
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/layoutServiceEdit', globals(),  __name__='manage_editForm')

    security.declareProtected('View management screens', 'manage_main')
    manage_main = manage_editForm

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._refresh_datetime = DateTime()
        self._used_layouts = {}
        
    # MANIPULATORS

    security.declareProtected('View management screens', 'install')
    def install(self, name, REQUEST=None):
        """Install layout
        """
        layoutRegistry.install(self.get_root(), name)
        msg = "%s installed" % name
        if REQUEST is not None:
            return self.manage_main(manage_tabs_message=msg)

    security.declareProtected('View management screens', 'uninstall')
    def uninstall(self, name, REQUEST=None):
        """Uninstall extension
        """
        layoutRegistry.uninstall(self.get_root(), name)
        msg = "%s uninstalled" % name
        if REQUEST is not None:
            return self.manage_main(manage_tabs_message=msg)

    security.declareProtected('View management screens', 'refresh')

    def refresh(self, name):
        """Refresh (uninstall/install) extension.
        """
        self.uninstall(name)
        self.install(name)
        self._refresh_datetime = DateTime()
        msg = "%s refreshed" % name
        return self.manage_main(manage_tabs_message=msg)

    security.declareProtected('View management screens', 'refresh_all')
    def refresh_all(self):
        """Refreshes all extensions
        """
        for name in self.get_installed_names():
            self.refresh(name)
        msg = 'All layouts have been refreshed'
        return self.manage_main(manage_tabs_message=msg)

    # ACCESSORS

    security.declareProtected('View management screens', 'get_names')
    def get_names(self):
        """Return registered extension names
        """
        list = layoutRegistry.get_names()
        list.sort()
        return list

    def get_installed_names(self):
        """Return installed extension names
        """
        return [name for name in self.get_names()
                if self.is_installed(name)]

    def show_layout_section(self):
        installed = self.get_installed_names()
        if len(installed) <= 1 and DEFAULT_LAYOUT in installed:
            return 0
        else:
            return 1

    NOLAYOUT = 'No own layout, get acquired'

    def get_installed_for_select(self):
        result = [(self.NOLAYOUT, '')]
        for name in self.get_installed_names():
            layout = layoutRegistry.get_layout(name)
            result.append((layout.description, name))
        return result

    security.declareProtected('View management screens', 'get_description')
    def get_description(self, name):
        """Return description of extension
        """
        return layoutRegistry.get_description(name)

    security.declareProtected('View management screens', 'is_installed')
    def is_installed(self, name):
        """Is extension installed?
        """
        return layoutRegistry.is_installed(self.get_root(), name)

    security.declareProtected('View management screens',
                              'get_refresh_datetime')
    def get_refresh_datetime(self):
        """Get datetime of last refresh.
        """
        return self._refresh_datetime

    # USED LAYOUTS

    def setup_layout(self, layout, publication):
        newUsedLayout = layoutRegistry.setup_layout(self.get_root(), layout, publication)
        if not publication.get_own_layout_key():
            publication.set_layout_key(self._get_unique_layout_key())
        self._used_layouts[publication.get_own_layout_key()] = newUsedLayout
        self._p_changed = 1

    def clone_layout(self, publication):
        old_key = publication.get_own_layout_key()
        if old_key:
            self.copy_used_layout(publication, old_key)

    def copy_used_layout(self, publication, key):
        publication.set_layout_key(self._get_unique_layout_key())
        newUsedLayout = copy.copy(self._used_layouts[key])
        self._used_layouts[publication.get_layout_key()] = newUsedLayout
        self._p_changed = 1

    def remove_layout(self, publication):
        used_layout = self.get_own_used_layout(publication)
        if used_layout:
            if used_layout.copied:
                layout_ids = [id for id in self.layout_ids(publication) if hasattr(publication.aq_base, id)]
                publication.manage_delObjects(layout_ids)

            del self._used_layouts[publication.get_layout_key()]
            self._p_changed = 1
            publication.set_layout_key(None)
        
    def _get_unique_layout_key(self):
        unique = str(random.random())
        while self._used_layouts.has_key(unique):
            unique = str(random.random())
        return unique

    def has_layout(self, publication):
        return self._used_layouts.has_key(publication.get_layout_key())

    def has_own_layout(self, publication):
        return self._used_layouts.has_key(publication.get_own_layout_key())

    def get_layout_name(self, publication):
        used_layout = self.get_used_layout(publication)
        if used_layout: 
            return used_layout.name
        else:
            return ''

    def get_own_layout_name(self, publication):
        used_layout = self.get_own_used_layout(publication)
        if used_layout: 
            return used_layout.name
        else:
            return ''

    def get_used_layout(self, publication):
        if self.has_layout(publication):
            return self._used_layouts[publication.get_layout_key()]
        else:
            return None

    def get_own_used_layout(self, publication):
        if self.has_own_layout(publication):
            return self._used_layouts[publication.get_own_layout_key()]
        else:
            return None

    def get_layout_folder(self, publication):
        if self.has_layout(publication):
            if not self.layout_copied(publication):
                layout_name = self.get_layout_name(publication)
                return layoutRegistry.get_layout_folder(self.get_root(), layout_name)
            else:
                return publication
        else:
            return None

    def get_layout_description(self, publication):
        if self.has_layout(publication):
            layout_name = self.get_layout_name(publication)
            return layoutRegistry.get_layout_description(self.get_root(), layout_name)
        else:
            return ''

    def layout_copied(self, publication):
        used_layout = self.get_used_layout(publication)
        if used_layout: 
            return used_layout.copied
        else:
            return 0

    def layout_items(self, publication):
        used_layout = self.get_used_layout(publication)
        if used_layout is None:
            return []
        else:
            return layoutRegistry.layout_ids(self.get_root(), used_layout.name)

    def copy_layout(self, publication):
        layout_name = self.get_layout_name(publication)
        layoutRegistry.copy_layout(self.get_root(), layout_name, publication)       
        if not self.has_own_layout(publication):
            old_key = publication.get_layout_key()
            self.copy_used_layout(publication, old_key)
        used_layout = self.get_own_used_layout(publication)
        used_layout.copied = 1
        self._p_changed = 1
            

    def layout_ids(self, publication):
        return self.layout_items(publication)
    
InitializeClass(LayoutService)

manage_addLayoutServiceForm = PageTemplateFile(
    "www/layoutServiceAdd", globals(), __name__='manage_addLayoutServiceForm')

def manage_addLayoutService(self, id, title='', REQUEST=None):
    """Add extension service."""
    object = LayoutService(id, title)    
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
