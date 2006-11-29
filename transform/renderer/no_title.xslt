<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content silva-extra"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://infrae.com/ns/silva"
  xmlns:silva-content="http://infrae.com/namespaces/metadata/silva"
  version="1.0">
  <xsl:import href="%(url)s/doc_elements.xslt"/>
  <xsl:output method="xml" omit-xml-declaration="yes" indent="yes"/>

  <xsl:template match="/">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:silva_document">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="doc:doc">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="silva:metadata" />
  
  <xsl:template match="silva:workflow" />
  
</xsl:stylesheet>
