<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://infrae.com/ns/silva"
  xmlns:silva-content="http://infrae.com/namespaces/metadata/silva"
  version="1.0">
  <xsl:import href="%(url)s/doc_elements.xslt"/>

  <xsl:template match="/">
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

  <xsl:template match="silva:silva_document">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:content">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="doc:doc">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:metadata">
    <h2 class="heading">
      <xsl:value-of select="silv:set[@id='silva-content']/silva-content:maintitle" />
    </h2>
  </xsl:template>

  <xsl:template match="doc:image" />

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

</xsl:stylesheet>
