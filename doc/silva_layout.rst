----------------------
Silva layout packages
----------------------

Support for using layout packages for public view of Silva content is
described hereunder in the user and the developer perspectives.


User perspective
++++++++++++++++

This section will describe how to use the functionality.

Layouts are packaged as Zope products. They are made of Page templates, CSS
images on the file system. By installing a product containing
layout packages, those packages get registered in Silva. They are then available to be installed. Before being installed, a layout package cannot be used inside Silva.

To install one of those packages in a Silva root, you need to use the ZMI for
the root, access the ``Services`` tab, and access the ``service_layouts``. Over there, registered layouts are listed and you can install (or uninstall) each of them for the root you are in.

When at least one layout package has been installed, a layout section appears
in the properties tab of the SMI of publications. Over there, you can select
one of the packages as the layout of the public view for the content of the publication. 

When one of those package is selected for a publication, you get a
supplementary button in the layout section of the SMI. This button
allows you to customize the layout. What it actually does is to copy the
elements of the layout package (HTML through ZPT, CSS, images...) inside the
publication itself. This way, you can modify those elements by accessing them
through the ZMI. 

Developer perspective
+++++++++++++++++++++

This section will describe how to create a layout package in a Zope product.

A reference implementation is found in the SilvaInfraeLayouts module at
http://cvs.infrae.com

Such a product is a Python package : it contains ``__init__.py`` file. This is
where the registration of the layout packages.
Let's check what is found in this file::

  from Products.Silva.LayoutRegistry import layoutRegistry
  def initialize(context):
      layoutRegistry.register(
          'Infrae1', 'Infrae First Layout', __file__, 'Infrae1')
      layoutRegistry.register(
          'Infrae2b', 'Infrae Second Layout', __file__, 'Infrae2b')

The insteresting line is the call to the ``register`` method of the
``LayoutRegistry``. This call has four arguments : 

- an id, that must be unique among the system
- a title that will appear in the SMI select box.
- a root directory name
- a directory name, relative to the root. The two last parameters are combined
  in an absolute path which is the directory that will be registered as a 
  FileSystem Directory View. This directory will contain the elements composing
  the layout : ZPT, CSS, images, subdirectories,...

As stated above, package registration is the registration is actually
registration of file system elements. The required aspects of those elements
are described hereunder.

There must be a ZPT file that will be imported as ``content.html`` in the top
directory of the package (ie ``content.html.pt``).

The Silva contents are passed to the template through the ``options/model``
variable. What this implies for the template developer is that the title of
the data will be accessible through ``options/model/title`` and not through 
``here/title`` as usual in standard Zope. A recommended practice is thus to
define a top variable : ``tal:define="model options/model"``. This allows the
use of the shorter ``model/title`` in place of ``options/model/title``.

