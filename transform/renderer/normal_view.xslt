<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content silva-extra"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://infrae.com/ns/silva"
  xmlns:silva-content="http://infrae.com/namespaces/metadata/silva"
  version="1.0">
  <xsl:import href="%(url)s/doc_elements.xslt"/>
  <xsl:output method="html" indent="yes"/>

  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:silva_document">
    <xsl:comment>xslt renderer used</xsl:comment>
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="doc:doc">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:metadata">
    <h2 class="heading">
      <xsl:value-of select="silva:set[@id='silva-content']/silva-content:maintitle" />
    </h2>
  </xsl:template>

</xsl:stylesheet>
