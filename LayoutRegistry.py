# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.4 $

from Products.Silva import icon
from Products.Silva.install import add_fss_directory_view
from Products.Silva.fssite import registerDirectory
import os

class LayoutRegistry:

    def __init__(self):
        self._layouts_order = []
        self._layouts = {}

    # MANIPULATORS

    def register(self, name, description, module, template_directory):
        self._layouts[name] = Layout(
            name, description, module, template_directory)
        registerDirectory(os.path.join(os.path.dirname(module), template_directory), globals())
        

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
        return self._layouts[name]
    
    def setup_layout(self, root, name, folder):
        directory = self.get_layout(name).directory
        template = getattr(root.service_resources.Layouts, directory)
        items = template.objectValues()
        folder_path = '/'.join(
            folder.getPhysicalPath()[len(root.getPhysicalPath()):])
        for item in items:
            item.manage_doCustomize(folder_path, root=root)

    def layout_items(self, root, name):
        directory = self.get_layout(name).directory
        template = getattr(root.service_resources.Layouts, directory)
        return template.objectIds()

class Layout:
    def __init__(self, name, description, module, template_directory):
        self.name = name
        self.description = description
        self.module = module
        self.directory = template_directory

    def is_installed(self, root):
        return hasattr(root, self.directory)

    def install(self, root):
        add_fss_directory_view(
            root, self.directory, self.module, self.directory)

    def uninstall(self, root):
        root.manage_delObjects([self.directory])


layoutRegistry = LayoutRegistry()
