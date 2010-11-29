<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
   exclude-result-prefixes="doc silva silva-content silva-extra"
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   xmlns:doc="http://infrae.com/namespace/silva-document"
   xmlns:silva="http://infrae.com/namespace/silva"
   xmlns:silva-content="http://infrae.com/namespace/metadata/silva-content"
   xmlns:silva-extra="http://infrae.com/namespace/metadata/silva-extra"
   version="1.0">

  <!--
     An example of an alternative stylesheet for rendering Silva Documents.
     The above namespaces should not be changed. They could be added to for
     those who have extended Silva Document XML and used their own namespace.
    -->

  <xsl:import href="silvabase:doc_elements.xslt"/>

  <xsl:output
     method="xml"
     omit-xml-declaration="yes"
     indent="no"
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
          <xsl:apply-templates />
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

  <xsl:template match="doc:image">
    <xsl:if test="ancestor::doc:table">
      <xsl:apply-templates select="." mode="image-content" />
    </xsl:if>
  </xsl:template>

  <xsl:template match="doc:link">
    <xsl:if test="ancestor::doc:table">
      <xsl:variable name="image" select="doc:image" />
      <a href="{@href|@url}" title="{@title}" target="{@target}">
        <xsl:apply-templates mode="image-content" />
      </a>
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

  <xsl:template match="doc:image" mode="images">
    <xsl:apply-templates select="." mode="image-content" />
    <br />
  </xsl:template>

  <xsl:template match="doc:link" mode="images">
    <xsl:variable name="image" select="doc:image" />
    <a href="{@href|@url}" title="{@title}" target="{@target}">
      <xsl:apply-templates mode="image-content" />
    </a>
    <br />
  </xsl:template>

</xsl:stylesheet>
