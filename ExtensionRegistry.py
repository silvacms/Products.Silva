# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.12 $

from bisect import insort_right

import Products

from Products.Silva import icon
from Products.Silva.interfaces import ISilvaObject


class Addable:

    def __init__(self, meta_type, priority=0.0):
        self._meta_type = meta_type
        self.priority = priority
        
    def __cmp__(self, other):
        sort = cmp(self.priority, other.priority)
        if sort == 0:
            sort = cmp(self._meta_type['name'], other._meta_type['name'])
        return sort
        

class ExtensionRegistry:

    def __init__(self):
        self._extensions_order = []
        self._extensions = {}
        self._silva_addables = []

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
        klass = getattr(module, classname)
        version_classname = classname + 'Version'
        __traceback_info__ = (module, classname, version_classname)
        meta_type = klass.meta_type
        # The order of the items in the contents screen new list is
        # determined by the addable_priority, defined in each item's
        # py file. Might be better if this was centrally defined.
        # Silva News items begin at 3 (the current bottom).
        priority = getattr(module, 'addable_priority', 0)
        # Register Silva Addable
        context.registerClass(
            klass,
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
        icon_path = getattr(module, 'icon', None)
        if icon_path:
            icon.registry.registerIcon(
                ('meta_type', meta_type),
                icon_path,
                module.__dict__)
        if ISilvaObject.implementedBy(klass):
            for i in range(len(self._silva_addables)):
                if self._silva_addables[i]._meta_type['name'] == meta_type:
                    del(self._silva_addables[i])
                    break
            self.addAddable(meta_type, priority)
   
    def addAddable(self, meta_type, priority):
        """Allow adding an addable to silva without using the
        registerClass shortcut method.
        """
        meta_types = Products.meta_types
        for mt_dict in meta_types:
            if mt_dict['name'] == meta_type:
                insort_right(self._silva_addables, Addable(mt_dict,
                     priority))
        
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

    def get_product_module_name(self, name):
        install_module = self._extensions[name][1]
        module_name = install_module.__name__
        # module_name is something like Products.Silva.install
        return module_name.split('.')[1]
    
    def is_installed(self, name, root):
        if not self._extensions.has_key(name):
            return 0
        return self._extensions[name][1].is_installed(root)

    def get_depends_on(self, name):
        return self._extensions[name][2]

    def get_addables(self):
        return [ addable._meta_type for addable in self._silva_addables ]

extensionRegistry = ExtensionRegistry()

