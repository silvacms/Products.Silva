==================================================
How To Make Your Own Renderer For Silva Documents.
==================================================

:Author: Eric Casteleijn


1. The Stylesheet
=================

This is 90% of the work really, and should be handled with
care. Stylesheets that are syntactically incorrect may in some cases
cause strange behaviour in Python/Zope, since the bindings for
libxml2/libxslt are not as robust at error handling as we'd like them
to be. When you want to test your stylesheet for the first time, it
may be a good idea to validate it outside of Zope first, and perhaps
even to run a test transformation on an export of a Silva Document
with xsltproc.

Building the stylesheet can be very simple or very complicated depending
on what you want it to do. For a relatively simple documented example
see images_to_the_right.xslt::

 <?xml version="1.0" encoding="UTF-8" ?>
 <xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://infrae.com/ns/silva"
  xmlns:silva-content="http://infrae.com/namespaces/metadata/silva"
  version="1.0">

 <!--
  An example of an alternative stylesheet for rendering Silva Documents.
  The above namespaces should not be changed. They could be added to for
  those who have extended Silva Document XML and used their own namespace.
  -->


 <!--
  This is hackish, but no other way was found to get the relative
  url of the two stylesheets right. The xsl:import is weird in this, IMHO.
  Python uses a string interpolation to get the right url. This also
  should probably not be changed. This import gets the document with
  the normal renderers for all the xml elements that can occur in a
  Silva Document. These renderers are then overridden in this file.
  No changes should be made to doc_elements.xslt.
  -->

  <xsl:import href="%(url)s/doc_elements.xslt"/>

 <!--
  In this example we want to render all content in in two table cells.
  The right one containing all images in order, and the left one containing
  everything else. The match="/" matches the document element of the
  Silva xml (usually <silva>) and starts to build the html from there.
  -->

  <xsl:template match="/">
    <table>
      <tr>
        <td valign="top">
          <xsl:apply-templates/>
        </td>
        <td valign="top">
          <xsl:apply-templates mode="images" />
        </td>
      </tr>
    </table>
  </xsl:template>

 <!--
  Nothing special needs to be done with silva_document or content for our
  purposes here but it could for your own renderer.
  -->

  <xsl:template match="silva:silva_document">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:content">
    <xsl:apply-templates />
  </xsl:template>

 <!--
  The real content of the document begins here.
  -->

  <xsl:template match="doc:doc">
    <xsl:apply-templates />
  </xsl:template>

 <!--
  The metadata is ignored, except for the title. You can access all
  metadata fields here in the same manner.
  -->

  <xsl:template match="silva:metadata">
    <h2 class="heading">
      <xsl:value-of select="silva:set[@id='silva-content']/silva-content:maintitle" />
    </h2>
  </xsl:template>

 <!--
  In the 'normal' mode i.e. no mode specified, used in the left table
  cell, all images are ignored.
  -->

  <xsl:template match="doc:image" />

  <!--
  In the 'images' mode (mode="images"), used in the right table
  cell, all text() nodes are ignored, and the images are shown, as
  links if they have a link attribute, as plain images, if not.
  -->

  <xsl:template match="text()" mode="images">
  </xsl:template>

  <xsl:template match="doc:image[@link]" mode="images">
    <a href="{@link}">
      <img src="{@path}" />
    </a>
    <br />
  </xsl:template>

  <xsl:template match="doc:image[not(@link)]" mode="images">
    <img src="{@path}" /><br />
  </xsl:template>

 <!--
  These are all the overrides needed, but one could quite easily pick
  certain elements and override them to render them differently. I would
  start with copying the xsl:template for the element from
  doc_elements.xslt to your own stylesheet, and modify it there until
  it does what you want.
  -->

 </xsl:stylesheet>

(To see how the normal rendering is done with XSLT, have a look at
normal_view.xslt.)

To create your own stylesheet, it may be useful to use
images_to_the_right.xslt or normal_view.xslt as starting points. Do
not modify doc_elements.xslt as that could break your renderer in
future versions of Silva, when new elements may be added.

There is plenty of good documentation on writing XSLT stylesheets on
the web and in print, and it really isn't all that hard.


2. The Renderer
===============

Once your stylesheet is done, you need to build a renderer that uses
it. For example take a look at imagesonrightrenderer.py::

 #!/usr/bin/python
 import os

 # Zope
 from Globals import InitializeClass

 # Silva
 from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase

 class ImagesOnRightRenderer(XSLTRendererBase):
     def __init__(self):
         XSLTRendererBase.__init__(self)

         # for creating your own renderer, copying this file, and
         # modifying the self._name and the filename of the stylesheet
         # should be enough

         self._name = 'Images on Right'
         self._stylesheet_path = os.path.join(
             os.path.dirname(os.path.abspath(__file__)),
             "images_to_the_right.xslt")
         self._stylesheet = None

 InitializeClass(ImagesOnRightRenderer)

All this really does is make a 'wrapper' for your stylesheet and gives
it a name to use in Silva, so that it can be registered.


3. Registering the Renderer
===========================

All you have to do now is register the renderer with Silva. This
happens in rendererreg.py. Add an import statement like::

 from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer

for your own renderer and modify the line::

 _REGISTRY = {'Silva Document Version' : [ImagesOnRightRenderer(), BasicXSLTRenderer()]}


4. Using the Renderer
=====================

There are two ways to use your renderer in Silva. For a specific
document you can switch between renderers in its metadata field
'content renderer'.  The preview, public preview and public view will
start using the selected renderer.

Content can also use a default renderer. You can set the default
renderer by going to the 'services' tab in your Silva root, clicking
on 'service renderer registry' and then the tab 'Default
Renderers'. Switching the default renderer for a type will affect all
content of that type in your Silva instance, for which "(Default)" is
the selected renderer.

Try switching the default renderer for Silva Document Version from
'Normal View (XMLWidgets)', that uses the old XMLWidget rendering
system to 'Normal View (XSLT)', that uses the fancy newfangled XSLT
rendering. The results should look 100% identical, but you may find
that the latter gives you a significant speed improvement, especially
for larger documents.
