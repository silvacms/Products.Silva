# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from zope.configuration.name import resolve
import Products

from bisect import insort_right

import os.path
import pkg_resources
import types
import icon
import interfaces

class Addable(object):

    def __init__(self, meta_type, priority=0.0):
        self._meta_type = meta_type
        self.priority = priority
        
    def __cmp__(self, other):
        sort = cmp(self.priority, other.priority)
        if sort == 0:
            sort = cmp(self._meta_type['name'], other._meta_type['name'])
        return sort

class BaseExtension(object):

    def __init__(self, name, install, description=None,
                 depends=(u'Silva',)):        
        self._name = name
        self._description = description
        self._install = install

        if depends and not (isinstance(depends, types.ListType) or
                            isinstance(depends, types.TupleType)):
            depends = (depends,)
        
        self._depends = depends

    @property
    def name(self):
        return self._name

    @property
    def product(self):
        return self._product

    @property
    def module_name(self):
        return self._product

    @property
    def module_directory(self):
        return os.path.dirname(self.module.__file__)
    
    @property
    def module(self):
        return resolve(self.module_name)
    
    @property
    def version(self):
        return self._version

    @property
    def description(self):
        return self._description

    @property
    def installer(self):
        return self._install

    @property
    def depends(self):
        return self._depends

    def get_content(self):
        result = []
        my_name = self.name
        for content in Products.meta_types:
            if content['product'] == my_name:
                result.append(content)
        return result

class ProductExtension(BaseExtension):
    """Extension based on a Zope product.
    """

    implements(interfaces.IExtension)

    def __init__(self, name, install, description=None,
                 depends=(u'Silva',)):
        super(ProductExtension, self).__init__(name, install,
                                               description, depends)
        install_name = install.__name__
        assert install_name.startswith('Products.')
        self._product = install_name.split('.')[1]

        product = resolve('Products.%s' % self._product)
        product_path = os.path.dirname(product.__file__)
        self._version = open(os.path.join(product_path, 'version.txt')).read()

    @property
    def module_name(self):
        return 'Products.%s' % self._product


class EggExtension(BaseExtension):
    """Extension package as an egg.
    """

    implements(interfaces.IExtension)

    def __init__(self, egg, name, install, description=None,
                 depends=(u'Silva',)):
        super(EggExtension, self).__init__(name, install,
                                           description, depends)
        # We assume that the name of this egg is the name of the python extension
        if egg.project_name.startswith('Products.'):
            self._product = egg.project_name.split('.', 1)[1]
        else:
            self._product = egg.project_name
        self._module_name = egg.project_name
        self._version = egg.version

    @property
    def module_name(self):
        return self._module_name

    
class ExtensionRegistry(object):

    implements(interfaces.IExtensionRegistry)

    def __init__(self):
        self._extensions_order = []
        self._extensions = {}
        self._extensions_by_module = {}
        self._silva_addables = []

    # MANIPULATORS

    def isEgg(self, installer):
        if isinstance(installer, types.ModuleType):
            path = installer.__file__
        else:
            path = resolve(installer.__module__).__file__
        for egg in pkg_resources.working_set:
            if (path.startswith(egg.location) and
                path[len(egg.location)] == os.path.sep):
                return egg
        return None

    def register(self, name, description, context, modules,
                 install_module, depends_on=(u'Silva',)):

        egg = self.isEgg(install_module)
        if egg is None:
            ext = ProductExtension(name, install_module, description, depends_on)
        else:
            ext = EggExtension(egg, name, install_module, description, depends_on)

        self._extensions[ext.name] = ext
        self._extensions_by_module[ext.module_name] = ext
        
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
        if interfaces.ISilvaObject.implementedBy(klass):
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
        for value in self._extensions.values():
            if not value.depends:
                depends_on_mapping.setdefault(None, []).append(value.name)
                continue
            for do in value.depends:
                depends_on_mapping.setdefault(do, []).append(value.name)
       
        # if depends_on is None, this should be first in the list
        added = depends_on_mapping.get(None, [])
       
        # now add them to the list and get dependencies in turn
        result = []
        while added:
            new_added = []
            for name in added:
                if name in result:
                    result.remove(name)
                result.append(name)
                new_added.extend(depends_on_mapping.get(name, []))
            added = new_added
        self._extensions_order = result

    def install(self, name, root):
        self._extensions[name].installer.install(root)
     
    def uninstall(self, name, root):
        self._extensions[name].installer.uninstall(root)

    # ACCESSORS

    def get_names(self):
        return self._extensions_order

    def get_extension(self, name):
        return self._extensions[name]

    def is_installed(self, name, root):
        if not self._extensions.has_key(name):
            return False
        return self._extensions[name].installer.is_installed(root)

    def get_name_for_class(self, class_):
        path = class_.__module__
        for module in self._extensions_by_module.keys():
            if (path.startswith(module) and
                (len(path) == len(module) or
                 path[len(module)] == '.')):
                return self._extensions_by_module[module].name
        return None

    def get_addables(self):
        return [ addable._meta_type for addable in self._silva_addables ]

extensionRegistry = ExtensionRegistry()

