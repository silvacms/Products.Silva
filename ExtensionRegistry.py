# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $

class ExtensionRegistry:

    def __init__(self):
        self._extensions_order = []
        self._extensions = {}

    # MANIPULATORS

    def register(
        self, name, description, context, modules, install_module, 
        depends_on='Silva'):

        self._extensions[name] = (description, install_module, depends_on)
        # try to order based on dependencies
        self._orderExtensions()

        for module in modules:
            self.registerClass(context, module)

    def registerClass(self, context, module):
        # We assume the class name to be identical to the module name
        classname = module.__name__.split('.')[-1]
        version_classname = classname + 'Version'
        # Register Silva Addable
        context.registerClass(
            getattr(module, classname),
            constructors = (
                getattr(module, 'manage_add%sForm' % classname),
                getattr(module, 'manage_add%s' % classname)),
                icon = getattr(module, 'icon', None)
            )
        # Register version object, if available
        if hasattr(module, version_classname):
            context.registerClass(
                getattr(module, version_classname),
                constructors = (
                    getattr(module, 'manage_add%sForm' % version_classname),
                    getattr(module, 'manage_add%s' % version_classname)),
                    )
    
    def _orderExtensions(self):
        """Reorder extensions based on depends_on constraints.
        """
        # make mapping from name depended on to names that depend on it
        depends_on_mapping = {}
        for key, value in self._extensions.items():
            depends_on_mapping.setdefault(value[2], []).append(key)
       
        # if depends_on is None, this should be first in the list
        added = depends_on_mapping.get(None, [])
       
        # now add them to the list and get dependencies in turn
        result = []
        while added:
            result.extend(added)
            new_added = []
            for name in added:
                new_added.extend(depends_on_mapping.get(name, []))
            added = new_added
        self._extensions_order = result

    def install(self, name, root):
        self._extensions[name][1].install(root)
     
    def uninstall(self, name, root):
        self._extensions[name][1].uninstall(root)

    # ACCESSORS

    def get_names(self):
        return self._extensions_order

    def get_description(self, name):
        return self._extensions[name][0]

    def is_installed(self, name, root):
        return self._extensions[name][1].is_installed(root)

    def get_depends_on(self, name):
        return self._extensions[name][2]


extensionRegistry = ExtensionRegistry()