----------------------
Silva layout packages
----------------------

Support for using layout packages for public view of Silva content is
described hereunder in the user and the developer perspectives.


User perspective
++++++++++++++++

This section will describe how to use the functionality.

Layouts are packaged as Zope products. They are made of page templates, CSS,
images on the file system.  

When you install a product containing layout packages, those packages get
registered in Silva. They are then available to be installed. Before being
installed, a layout package cannot be used inside Silva.

To install one of those packages in a Silva root, you need to use the ZMI for
the root, access the ``Services`` tab, and access the ``service_layouts``.
Over there, registered layouts are listed and you can install (or uninstall)
each of them for the root you are in. In other words, different Silva roots
sharing the same zope instance could have different layout packages installed.

When at least one layout package has been installed, a layout section appears
in the properties tab of the SMI for publications. Over there, you can select
one of the packages : this will set the layout of the public view for the
content of the publication.

When a layout package has been set for a publication, you get a supplementary
button in the layout section of the SMI. This button allows you to customize
the layout. What this button actually does is to copy the elements of the
layout package (HTML through ZPT, CSS, images...) inside the publication 
itself. This way, you can modify those elements by accessing them through the
ZMI. 

Developer perspective
+++++++++++++++++++++

This section will describe how to create a layout package in a Zope product.

A reference implementation is found in the SilvaInfraeLayouts module at
http://cvs.infrae.com

Such a product is a Python package : it contains a ``__init__.py`` module. 
This module is where the layout packages are registered.
Let's check what is found in this file::

  from Products.Silva.LayoutRegistry import layoutRegistry
  def initialize(context):
      layoutRegistry.register(
          'Infrae1', 'Infrae First Layout', __file__, 'Infrae1')
      layoutRegistry.register(
          'Infrae2b', 'Infrae Second Layout', __file__, 'Infrae2b')

The insteresting call is the call of the ``register`` method of the
``LayoutRegistry``. This call has four arguments : 

- a layout id, that must be unique among the system,
- a layout title, that will appear in the SMI select box,
- a root directory name,
- a directory name, relative to the root. Those two last parameters are combined
  in an absolute path which is the directory that will be registered as a 
  FileSystem Directory View. This directory actually contains the elements composing
  the layout : ZPT, CSS, images, subdirectories,...

As stated above, package registration is actually the registration of file system
elements. The constraints for those elements are described hereunder.

There must be a ZPT file that will be imported as ``content.html`` in the top
directory of the package (ie ``content.html.pt``).

The Silva contents are passed to this template through the ``options/model``
variable. What this implies for the template developer is that the title of
the data will be accessible through ``options/model/title`` and not through 
``here/title`` as usual in standard Zope. A recommended practice is thus to
define a top variable : ``tal:define="model options/model"``. This allows the
use of the shorter ``model/title`` in place of ``options/model/title``.

The content.html relies on a general macro for page layout. This macro (called
``layout``) is supposed to be found in a ZPT file called ``layout_macro.html``.
The silva error report mechanism relies also on this macro : iow, if the
``layout`` macro is found in the layout folder, it will be used for error
reporting which will ensure that the errors (like 404 not found) are presented 
in a look and feel coherent with the rest of the site !
very similar
