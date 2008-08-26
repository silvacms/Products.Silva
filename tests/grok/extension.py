# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

    >>> from Products.Silva.interfaces import IExtensionInstaller
    >>> from Products.Silva.ExtensionRegistry import extensionRegistry
    >>> import pdb ; pdb.set_trace()

  A extension is declared in __init__.py of a package:

    >>> grokkify('Products.Silva.tests.grok.extension_nopackage_fixture')
    Traceback (most recent call last):
        ...
    GrokError: Your extension Bad Extension is not defined in a package.

  A extension should have a installer:

    >>> grokkify('Products.Silva.tests.grok.extension_noinstaller')
    Traceback (most recent call last):
        ...  
    GrokError: You need to define an installer for your extension Test Extension.

  But you can use the default installer from silva.core.conf.installer:

    >>> grokkify('Products.Silva.tests.grok.extension_simple')

  You can now look for your extension, and check its parameters and installer:

    >>> 'SimpleTestExtension' in extensionRegistry.get_names()
    True
    >>> my_extension = extensionRegistry.get_extension('SimpleTestExtension')
    >>> my_extension.name
    'SimpleTestExtension'
    >>> my_extension.description
    'Simple Test Extension'
    >>> my_extension.module_name
    'Products.Silva.tests.grok.extension_simple'
    >>> extension_iface = my_extension.module.ISimpleTestExtension
    >>> extension_iface
    <InterfaceClass Products.Silva.tests.grok.extension_simple.ISimpleTestExtension>
    >>> my_extension.installer
    <silva.core.conf.installer.DefaultInstaller object at ...>
    >>> verifyObject(IExtensionInstaller, my_extension.installer)
    True

  Since it's an extension, you can install it:

    >>> root = getSilvaRoot()
    >>> extensionRegistry.is_installed('SimpleTestExtension', root)
    False
    >>> extensionRegistry.install('SimpleTestExtension', root)
    >>> extensionRegistry.is_installed('SimpleTestExtension', root)
    True

  If you install an already installed extension, this should do nothing.

    >>> extensionRegistry.install('SimpleTestExtension', root)
    >>> extensionRegistry.is_installed('SimpleTestExtension', root)
    True

  Actually, the extension interface is set on the service_extensions
  by the default installer to mark the extension as installed:

    >>> extension_iface.providedBy(root.service_extensions)
    True

  And you can uninstall it:

    >>> extensionRegistry.uninstall('SimpleTestExtension', root)
    >>> extensionRegistry.is_installed('SimpleTestExtension', root)
    False
    >>> extension_iface.providedBy(root.service_extensions)
    False

  And if you uninstall an uninstalled extension, this does nothing.

    >>> extensionRegistry.uninstall('SimpleTestExtension', root)
    >>> extensionRegistry.is_installed('SimpleTestExtension', root)
    False


"""

