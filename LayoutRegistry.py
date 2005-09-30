# Copyright (c) 2003-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.12 $

from Products.Silva import icon
from Products.Silva.install import add_fss_directory_view
from Products.Silva.fssite import registerDirectory
import os
import md5
import cPickle

DEFAULT_LAYOUT = 'default'
DEFAULT_LAYOUT_DESCRIPTION = 'Default layout'
DEFAULT_LAYOUT_DIRECTORY = 'default'

class LayoutRegistry:

    def __init__(self):
        self._layouts_order = []
        self._layouts = {}

    # MANIPULATORS

    def register(self, name, description, module, directory, folder_id=None):
        if not folder_id:
            folder_id = directory
        self._layouts[name] = Layout(
            name, description, module, directory, folder_id)
        registerDirectory(os.path.join(os.path.dirname(module), directory), globals())
        

    def install(self, root, name):
        self._layouts[name].install(root.service_resources.Layouts)
     
    def uninstall(self, root, name):
        self._layouts[name].uninstall(root.service_resources.Layouts)

    # ACCESSORS

    def get_names(self):
        return self._layouts.keys()

    def get_description(self, name):
        return self._layouts[name].description

    def is_installed(self, root, name):
        return  self._layouts[name].is_installed(root.service_resources.Layouts)

    def get_layout(self, name):
        return self._layouts.get(name, None)
    
    def setup_layout(self, root, name, publication):
        newUsedLayout = usedLayout(name)
        return newUsedLayout

    def copy_layout(self, root, name, publication):
        if publication is root:
            publication_path = '.'
        else:    
            publication_path = '/'.join(
                publication.getPhysicalPath()[len(root.getPhysicalPath()):])
        folder = self.get_layout_folder(root, name)
        for item in folder.objectValues():
            item.manage_doCustomize(publication_path, root=root)

    def get_layout_folder(self, root, name):
        layout = self.get_layout(name)
        if layout:
            folder_id = layout.folder_id
            return getattr(root.service_resources.Layouts, folder_id)
        else:
            return None

    def get_layout_description(self, root, name):
        layout = self.get_layout(name)
        if layout:
            return layout.description
        else:
            return ''

    def layout_ids(self, root, name):
        folder = self.get_layout_folder(root, name)
        return folder.objectIds()

layoutRegistry = LayoutRegistry()

class Layout:
    def __init__(self, name, description, module, directory, folder_id):
        self.name = name
        self.description = description
        self.module = module
        self.directory = directory
        self.folder_id = folder_id

    def is_installed(self, root):
        return hasattr(root, self.folder_id)

    def install(self, root):
        add_fss_directory_view(
            root, self.folder_id, self.module, self.directory)

    def uninstall(self, root):
        root.manage_delObjects([self.folder_id])

class usedLayout:
    
    def __init__(self, name):
        self.name = name
        self.copied = 0


