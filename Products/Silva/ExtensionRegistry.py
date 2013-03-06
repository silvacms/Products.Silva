# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from bisect import insort_right
from itertools import imap
import email
import os.path
import pkg_resources
import types

from five import grok
from silva.core import interfaces
from zope.configuration.name import resolve
from zope.interface import implements
from silva.core.interfaces import ISilvaObject

import Products


def filter_types_for_interfaces(types, requires, excepts):
    """Filter Zope meta_types to require or prevent one implementing
    an interface.
    """
    filter_type = lambda cls, ifcs: imap(lambda i: i.implementedBy(cls), ifcs)

    def filter_types(cls):
        cls = cls['instance']
        return ((not requires or any(filter_type(cls, requires))) and
                not (excepts and any(filter_type(cls, excepts))))

    return filter(filter_types, types)


def meta_types_for_interface(interface, excepts=[]):
    """Return a list of meta_type who implements the given interface.
    """
    addables = Products.meta_types
    if interface.extends(ISilvaObject):
        addables = extensionRegistry.get_addables()
    return [addable['name'] for addable in
            filter_types_for_interfaces(addables, [interface], excepts)]


def _get_product_meta_type(content_type):
    for mt_dict in Products.meta_types:
        if mt_dict['name'] == content_type:
            mt_dict['doc'] = mt_dict['instance'].__doc__
            return mt_dict
    return None


class Addable(object):

    def __init__(self, meta_type, content_type, priority=0.0):
        # meta_type is the main class, content_type the version class
        self.meta_type = meta_type
        self.priority = priority
        self.content_type = content_type

    def __cmp__(self, other):
        sort = cmp(self.priority, other.priority)
        if sort == 0:
            sort = cmp(self.meta_type['name'], other.meta_type['name'])
        return sort


class BaseExtension(object):
    """Base for extensions.
    """

    def __init__(self, name, install, path,
                 title=None, description=None, depends=(u'Silva',)):
        self._name = name
        self._title = title or name
        self._description = description
        self._install = install
        self._module_name = path

        if depends and not (isinstance(depends, types.ListType) or
                            isinstance(depends, types.TupleType)):
            depends = (depends,)

        self._depends = depends

    @property
    def name(self):
        return self._name

    @property
    def title(self):
        return self._title

    @property
    def product(self):
        return self._product

    @property
    def module_name(self):
        return self._module_name

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
        # XXX Maybe rename that to get_content_types.
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

    def __init__(self, name, install, path,
                 title=None, description=None, depends=(u'Silva',)):
        super(ProductExtension, self).__init__(
            name, install, path, title, description, depends)
        assert path.startswith('Products.')
        self._product = path.split('.')[1]
        self._version = open(os.path.join(
                self.module_directory, 'version.txt')).read()

    @property
    def module_name(self):
        return 'Products.%s' % self._product


class EggExtension(BaseExtension):
    """Extension package as an egg.
    """
    implements(interfaces.IExtension)

    def __init__(self, egg, name, install, path, title=None,
                 description=None, depends=(u'Silva',)):
        if description is None:
            info = email.message_from_string(egg.get_metadata('PKG-INFO'))
            description = info.get('Summary')
        super(EggExtension, self).__init__(
            name, install, path, title, description, depends)
        # We assume that the name of this egg is the name of the
        # python extension.
        if path.startswith('Products.'):
            self._product = path.split('.', 1)[1]
        else:
            self._product = path
        self._module_name = path
        self._version = egg.version

    @property
    def module_name(self):
        return self._module_name


class ExtensionRegistry(object):
    grok.implements(interfaces.IExtensionRegistry)

    def __init__(self):
        self.clear_registry()

    # MANIPULATORS

    def clear_registry(self):
        """Clear the registry. *Don't call this in regular order of operation*.
        """
        self._extensions_order = []
        self._extensions = {}
        self._extensions_by_module = {}
        self._silva_addables = []

    def register(self, name, title,
                 install_module=None, module_path=None, depends_on=(u'Silva',)):
        # Figure out which is the extension path.
        path = None
        assert not ((install_module is None) and (module_path is None))
        if module_path:
            path = resolve(module_path).__file__
        elif isinstance(install_module, types.ModuleType):
            # Installer is a module install.py which HAVE TO BE in the
            # extension package.
            module_path = '.'.join(install_module.__name__.split('.')[:-1])
            path = install_module.__file__
        else:
            # Installer is a class in the __init__.py of the extension.
            module_path = install_module.__module__
            path = resolve(module_path).__file__

        assert os.path.exists(path)

        # Remove any symbolic links encountered (like setuptools)
        path = os.path.realpath(path)

        # Search throught eggs to see if extension is an egg.
        ext = None
        for egg in pkg_resources.working_set:
            if (path.startswith(egg.location) and
                path[len(egg.location)] == os.path.sep):
                ext = EggExtension(
                    egg, name, install_module, module_path,
                    title, None, depends_on)
                break

        # Otherwise, that's a product.
        if ext is None:
            ext = ProductExtension(
                name, install_module, module_path,
                title, None, depends_on)

        self._extensions[ext.name] = ext
        self._extensions_by_module[ext.module_name] = ext

        # Try to order based on dependencies
        self._orderExtensions()

    def add_addable(self, meta_type, priority, content_type):
        """Allow adding an addable to silva without using the
        registerClass shortcut method.
        """
        meta_type = _get_product_meta_type(meta_type)
        if content_type is not None:
            content_type = _get_product_meta_type(content_type)
        else:
            content_type = meta_type
        if meta_type is not None and content_type is not None:
            insort_right(
                self._silva_addables,
                Addable(meta_type, content_type, priority))

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
        extension = self._extensions[name]
        extension.installer.install(root, extension)

    def uninstall(self, name, root):
        extension = self._extensions[name]
        extension.installer.uninstall(root, extension)

    def refresh(self, name, root):
        extension = self._extensions[name]
        if hasattr(extension.installer, 'refresh'):
            # installer has a refresh, so use it note: the default
            # refresh (in silva.core.conf.installer.DefaultInstaller)
            # is to just uninstall/install.  Extensions may choose to
            # override this to do a custom uninstall/install which may,
            # e.g. not remove a special service_<extension> object
            # which contains site-specific customizations
            extension.installer.refresh(root, extension)
        else:
            extension.installer.uninstall(root, extension)
            extension.installer.install(root, extension)

    # ACCESSORS

    def get_names(self):
        return self._extensions_order

    def get_extension(self, name):
        return self._extensions.get(name, None)

    def is_installed(self, name, root):
        extension = self.get_extension(name)
        if extension:
            return extension.installer.is_installed(root, extension)
        return False

    def get_name_for_class(self, cls):
        path = cls.__module__
        for module in self._extensions_by_module.keys():
            if (path.startswith(module) and
                (len(path) == len(module) or
                 path[len(module)] == '.')):
                return self._extensions_by_module[module].name
        return None

    def get_addables(self, requires=None, excepts=None):
        addables =  [addable.meta_type for addable in self._silva_addables]
        if any((requires, excepts)):
            return filter_types_for_interfaces(addables, requires, excepts)
        return addables

    def get_contents(self, requires=None, excepts=None):
        contents = [addable.content_type for addable in self._silva_addables]
        if any((requires, excepts)):
            return filter_types_for_interfaces(contents, requires, excepts)
        return contents

    def get_addable(self, content_type):
        for addable in self._silva_addables:
            if content_type == addable.meta_type['name']:
                return addable.meta_type
        return {}


extensionRegistry = ExtensionRegistry()

# Cleanup registry on layer tearDown
try:
    from infrae.testing import layerCleanUp
except ImportError:
    pass
else:
    layerCleanUp.add(extensionRegistry.clear_registry)
