# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $

from Products.Silva import icon
from Products.Silva.install import add_fss_directory_view

class LayoutRegistry:

    def __init__(self):
        self._layouts_order = []
        self._layouts = {}

    # MANIPULATORS

    def register(
        self, name, description, module, template_directory):

        self._layouts[name] = Layout(name, description, module, template_directory)

    def install(self, name, root):
        self._layouts[name].install(root)
     
    def uninstall(self, name, root):
        self._layouts[name].uninstall(root)

    # ACCESSORS

    def get_names(self):
        return self._layouts.keys()

    def get_description(self, name):
        return self._layouts[name].description

    def is_installed(self, name, root):
        return  self._layouts[name].is_installed(root)

    def get_layout(self, name):
        return self._layouts[name]
    

class Layout:
    def __init__(self, name, description, module, template_directory):
        self.name = name
        self.description = description
        self.module = module
        self.directory = template_directory

    def is_installed(self, root):
        return hasattr(root, self.directory)

    def install(self, root):
        add_fss_directory_view(root, self.directory, self.module, self.directory)

    def uninstall(self, root):
        root.manage_delObjects([self.directory])

    def setup(self, root, folder):
        template = getattr(root.service_resources.Layouts, self.directory)
        items = template.objectValues()
        folder_path = '/'.join(folder.getPhysicalPath()[len(root.getPhysicalPath()):])
        for item in items:
            item.manage_doCustomize(folder_path, root=root)

layoutRegistry = LayoutRegistry()
