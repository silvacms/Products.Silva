import os

from zope.configuration.name import resolve
import Products
from Interface.Implements import instancesOfObjectImplements
from zope.interface import implementedBy
from AccessControl.PermissionRole import PermissionRole
from App.ProductContext import AttrDict
from App.FactoryDispatcher import FactoryDispatcher
import AccessControl.Permission
import Globals
from OFS import misc_ as icons
from Products.Five.fiveconfigure import unregisterClass

from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.Silva.fssite import registerDirectory
from Products.Silva.icon import registry as icon_registry
from Products.Silva import mangle
from Products.Silva.helpers import add_and_edit, makeContainerFilter
from Products.Silva.interfaces import ISilvaObject

def extension(_context, name, title, depends=(u"Silva",)):
    """The handler for the silva:extension directive.

    See .directives.IExtensionDirective
    
    Defers its implementation to registerExtension.
    """
    _context.action(
        discriminator=name,
        callable=registerExtension,
        args=(name, title, depends),
        )

def registerExtension(name, title, depends):
    """Register a Silva extension.
    """
    install_module = resolve('Products.%s.install' % name)
    # since we don't pass in any modules for automatic class
    # registration, we don't need a context either
    if not depends:
        depends = None
    extensionRegistry.register(
        name, title, context=None, modules=[], install_module=install_module,
        depends_on=depends)

    product = resolve('Products.%s' % name)
    registerDirectory('views', getProductDir(product))

def content(_context, extension_name, content, priority=0, icon=None,
            content_factory=None, zmi_addable=False):
    """The handler for the silva:content directive.

    See .directives.IContentDirective

    Defers its implementation to registerContent.
    """
    _context.action(
        discriminator=(content,),
        callable=registerContent,
        args=(extension_name, content, priority, icon, content_factory, zmi_addable),
        )

def registerContent(extension_name, content, priority, icon, content_factory, zmi_addable):
    """Register content type.
    """
    registerClass(content, extension_name, zmi_addable)

    product = resolve('Products.%s' % extension_name)

    methods = getProductMethods(product)

    if content_factory is None:
        content_factory = ContentFactory(content)

    registerFactory(methods, content, content_factory)

    registerIcon(product, extension_name, content, icon)
    # make sure we can add silva metadata to it
    registerTypeForMetadata(content.meta_type)
    # make it show up in the Silva addables list
    extensionRegistry.addAddable(content.meta_type, priority)
    
def versionedcontent(_context, extension_name, content, version, priority=0,
                     icon=None, content_factory=None, version_factory=None, zmi_addable=False):
    """The handler for the silva:versionedcontent directive.

    See .directives.IVersionedContentDirective
    
    Defers its implementation to registerVersionedContent.
    """
    _context.action(
        discriminator=(content, version),
        callable=registerVersionedContent,
        args=(extension_name, content, version, priority, icon,
              content_factory, version_factory, zmi_addable),
        )

def registerVersionedContent(extension_name, content, version, priority,
                             icon, content_factory, version_factory, zmi_addable):
    """Register a versioned content type and the implementation of its version.
    """
    
    registerClass(content, extension_name, zmi_addable)
    registerClass(version, extension_name, zmi_addable)

    product = resolve('Products.%s' % extension_name)

    methods = getProductMethods(product)

    if content_factory is None:
        content_factory = VersionedContentFactory(extension_name,
                                                  content, version)
    registerFactory(methods, content, content_factory)
    if version_factory is None:
        version_factory = VersionFactory(version)
    registerFactory(methods, version, version_factory)

    registerIcon(product, extension_name, content, icon)
    # make sure we can add silva metadata to it
    registerTypeForMetadata(version.meta_type)
    # make it show up in the Silva addables list
    extensionRegistry.addAddable(content.meta_type, priority)

def getFactoryDispatcher(product):    
    """Get the Factory Dispatcher, some Zope 2 magic.
    """
    fd = getattr(product, '__FactoryDispatcher__', None)
    if fd is None:
        class __FactoryDispatcher__(FactoryDispatcher):
            "Factory Dispatcher for a Specific Product"
            
        fd = product.__FactoryDispatcher__ = __FactoryDispatcher__
    return fd

def getProductMethods(product):
    """Get the methods dictionary for a product.

    This can be used to register product-level methods, such as factory
    functions like manage_addFoo.
    """
    try:
        return product._m
    except AttributeError:
        fd = getFactoryDispatcher(product)
        product._m = result = AttrDict(fd)
        return result

def registerIcon(product, extension_name, class_, icon):
    """Register icon for a class.
    """
    if not icon:
        return
    
    name = os.path.basename(icon)
    icon = Globals.ImageFile(icon, getProductDir(product))
    icon.__roles__ = None
    if not hasattr(icons.misc_, extension_name):
        setattr(icons.misc_, extension_name,
                icons.Misc_(extension_name, {}))
    getattr(icons.misc_, extension_name)[name] = icon
    icon_path = 'misc_/%s/%s' % (extension_name, name)
    
    icon_registry._icon_mapping[('meta_type', class_.meta_type)] = icon_path
    class_.icon = icon_path
    
def ContentFactory(content):
    """A factory for Content factories.

    This generates manage_add<Something> for non-versioned content types.
    """
    def factory_method(self, id, title, *args, **kw):
        container = self
        if not mangle.Id(container, id).isValid():
            return
        object = content(id)
        self._setObject(id, object)
        object = getattr(container, id)
        object.set_title(title)
        add_and_edit(container, id, None)
        return ''
    return factory_method

def VersionedContentFactory(extension_name, content, version):
    """A factory for Versioned Content factories.

    This generates manage_add<Something> for versioned content types. It
    makes sure the first version is already added.
    """
    def factory_method(self, id, title, *args, **kw):
        container = self
        if not mangle.Id(container, id).isValid():
            return
        object = content(id)
        container._setObject(id, object)
        object = getattr(container, id)

        version_factory_name = getFactoryName(version)

        version_factory = getattr(
            object.manage_addProduct[extension_name],
            version_factory_name)
        version_factory('0', title, *args, **kw)
        object.create_version('0', None, None)
        add_and_edit(container, id, None)
        return ''
    return factory_method

def VersionFactory(version_class):
    """A factory for Version factories.

    This generateas manage_add<Something>Version for versions.
    """
    def factory_method(self, id, title, *args, **kw):
        container = self
        version = version_class(id, *args, **kw)
        container._setObject(id, version)
        version = container._getOb(id)
        version.set_title(title)
        add_and_edit(container, id, None)
        return ''
    return factory_method

# for use in test cleanup
_register_monkies = []
_meta_type_regs = []

#visibility can be "Global" or None
def registerClass(class_, extension_name, zmi_addable=False):
    """Register a class with Zope as a type.
    """
    permission = getAddPermissionName(class_)
    interfaces = instancesOfObjectImplements(class_) + list(implementedBy(class_))

    #There are two ways to remove this object from the list,
    #by either specifying "visibility: none", in which case
    #the object is never visible (and copy support is broken)
    #or by specifying a container_filter, which can return true
    #if the container is an ISilvaObject.  I'm opting for the latter,
    #as at least the objects aren't addable from outside the Silva Root then.
    #Also, Products.Silva.Folder will override ObjectManager.filtered_meta_types
    #to also remove any ISilvaObject types from the add list
    info = {'name': class_.meta_type,
            'action': 'manage_main',
            'product': extension_name,
            'permission': permission,
            'visibility': "Global",
            'interfaces': interfaces,
            'instance': class_,
            'container_filter': makeContainerFilter(zmi_addable)
            }
    Products.meta_types += (info,)

    # register for test cleanup
    _register_monkies.append(class_)
    _meta_type_regs.append(class_.meta_type)

def registerFactory(methods, class_, factory):
    """Register a manage_add<Something> style factory method.
    """
    name = getFactoryName(class_)
    methods[name] = factory
    permission = getAddPermissionName(class_)
    default = ('Manager',)
    pr = PermissionRole(permission, default)
    AccessControl.Permission.registerPermissions(
            ((permission, (), default),))
    methods[name + '__roles__'] = pr
    # also stuff it into the module of the class so that it can be imported
    module = resolve(class_.__module__)
    setattr(module, name, factory)

def getAddPermissionName(class_):
    return 'Add %ss' % class_.meta_type

def getFactoryName(class_):
    return 'manage_add' + class_.__name__

def getProductDir(product):
    return os.path.split(product.__file__)[0]
        

def cleanUp():
    global _register_monkies
    for class_ in _register_monkies:
        unregisterClass(class_)
    _register_monkies = []

    global _meta_type_regs
    Products.meta_types = tuple([ info for info in Products.meta_types
                                  if info['name'] not in _meta_type_regs ])
    _meta_type_regs = []

from zope.testing.cleanup import addCleanUp
addCleanUp(cleanUp)
del addCleanUp
