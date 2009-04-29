<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content silva-extra"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://infrae.com/ns/silva"
  xmlns:silva-content="http://infrae.com/namespaces/metadata/silva"
  xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra"
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

  <xsl:import href="silvabase:doc_elements.xslt"/>

  <xsl:output 
    method="xml" 
    omit-xml-declaration="yes" 
    indent="yes" 
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" 
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" />
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

  <xsl:template match="silva:workflow" />
  
<!--
  In the 'normal' mode i.e. no mode specified, used in the left table
  cell, all images are ignored.

  A special case are images in tables. If we move those out to the
  right, the table layouts are messed up, so we keep the images there.
  -->

  <xsl:template match="doc:image[@rewritten_link]">
    <xsl:if test="ancestor::doc:table">
      <a href="{@rewritten_link}">
        <img src="{@rewritten_path}" />
      </a>
    </xsl:if>
  </xsl:template>

  <xsl:template match="doc:image[not(@rewritten_link)]">
    <xsl:if test="ancestor::doc:table">
      <img src="{@rewritten_path}" />
    </xsl:if>
  </xsl:template>
  
  <xsl:template match="doc:table" mode="images">
  </xsl:template>

  <!--
  In the 'images' mode (mode="images"), used in the right table
  cell, all text() nodes are ignored, and the images are shown, as
  links if they have a link attribute, as plain images, if not.
  -->
  
  <xsl:template match="text()" mode="images">
  </xsl:template>
    

  <xsl:template match="doc:image[@rewritten_link]" mode="images">
    <a href="{@rewritten_link}">
      <img src="{@rewritten_path}" />
    </a>
    <br />
  </xsl:template>

  <xsl:template match="doc:image[not(@rewritten_link)]" mode="images">
    <img src="{@rewritten_path}" /><br />
  </xsl:template>

<!--
  These are all the overrides needed, but one could quite easily pick
  certain elements and override them to render them differently. I would
  start with copying the xsl:template for the element from 
  doc_elements.xslt to your own stylesheet, and modify it there until
  it does what you want. 
  -->
  
</xsl:stylesheet>
