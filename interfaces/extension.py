# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface, Attribute


class IExtension(Interface):
    """An extension to Silva.
    """

    name = Attribute("Name")
    version = Attribute("Version")
    description = Attribute("Description")
    product = Attribute("Product name")
    installer = Attribute("Installer module")
    depends = Attribute("Dependancy to other modules")
    module = Attribute("Python package implementing")
    module_name = Attribute("Name of the python package")
    module_directory = Attribute("Physical directory where the module is located")

    def get_content():
        """Return ALL content class availables for this extension.
        """


class IExtensionInstaller(Interface):
    """A Silva extension installer.
    """

    def install(root):
        """Install the extension in root.
        """

    def uninstall(root):
        """Uninstall the extension in root.
        """

    def is_installed(root):
        """Return true if the extension is installed in root.
        """


class IExtensionRegistry(Interface):
    """Silva extension registry.
    """

    # MANIPULATORS

    def register(name, description, context, modules, install_module,
                 depends_on=(u'Silva',)):
        """Register a new extension.
        """
        
    def install(name, root):
        """Install this extension to the given Silva root.
        """
     
    def uninstall(name, root):
        """Uninstall this extension from the given Silva root.
        """

    # ACCESSORS

    def get_names():
        """Return available extensions names.
        """

    def get_extension(name):
        """Return the given extension.
        """

    def is_installed(name, root):
        """Tells you if the given product is installed in this root.
        """

    def get_name_for_class(class_):
        """Return the extension name to which belongs this class.
        """

    def get_addable():
        """Return all addables content.
        """

