<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
  exclude-result-prefixes="doc silva silva-content silva-extra"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:doc="http://infrae.com/ns/silva_document"
  xmlns:silva="http://infrae.com/ns/silva"
  version="1.0">
  <!--  
  For your own renderers for Silva Documents, import this stylesheet and
  override where necessary. It is better not to modify this stylesheet
  directly. See images_to_the_right.xslt for a documented example.
  -->
  
  <xsl:preserve-space elements="heading p pre li em strong super sub underline link" />
  
  <xsl:template match="doc:heading[@type='normal']">
    <h3 class="heading"><xsl:apply-templates mode="text-content" /></h3>
  </xsl:template>
  
  <xsl:template match="doc:heading[@type='sub']">
    <h4 class="heading"><xsl:apply-templates mode="text-content" /></h4>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subsub']">
    <h5 class="heading"><xsl:apply-templates mode="text-content" /></h5>
  </xsl:template>

  <xsl:template match="doc:heading[@type='paragraph']">
    <h6 class="heading"><xsl:apply-templates mode="text-content" /></h6>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subparagraph']">
    <h6 class="minor"><xsl:apply-templates mode="text-content" /></h6>
  </xsl:template>

  <xsl:template match="doc:p[@type='normal']">
    <p class="p"><xsl:apply-templates mode="text-content" /></p>
  </xsl:template>

  <xsl:template match="doc:p">
    <p class="{@type}"><xsl:apply-templates mode="text-content" /></p>
  </xsl:template>

  <xsl:template match="doc:list[@type='disc']">
    <ul class="disc">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>

  <xsl:template match="doc:list[@type='square']">
    <ul class="square">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>
  
  <xsl:template match="doc:list[@type='circle']">
    <ul class="circle">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>

  <xsl:template match="doc:list[@type='1']">
    <ol class="decimal">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:list[@type='I']">
    <ol class="upper-roman">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>
  
  <xsl:template match="doc:list[@type='i']">
    <ol class="lower-roman">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:list[@type='A']">
    <ol class="upper-alpha">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:list[@type='a']">
    <ol class="lower-alpha">
      <xsl:apply-templates mode="list" />
    </ol>
  </xsl:template>
  
  <!-- need IE support? -->
  <xsl:template match="doc:list[@type='none']">
    <ul class="nobullet">
      <xsl:apply-templates mode="list" />
    </ul>
  </xsl:template>

  <xsl:template match="doc:dlist">
    <dl class="dl">
      <xsl:if test="@type='compact'">
        <xsl:attribute name="compact">compact</xsl:attribute>
      </xsl:if>
      <xsl:apply-templates mode="dlist" />
    </dl>
  </xsl:template>
  
  <xsl:template match="doc:pre">
    <pre class="pre"><xsl:apply-templates mode="pre" /></pre>
  </xsl:template>
  
  <xsl:template match="doc:nlist[@type='disc']">
    <ul class="disc">
      <xsl:apply-templates mode="nlist" />
    </ul>
  </xsl:template>
  
  <xsl:template match="doc:li" mode="list">
    <li><xsl:apply-templates mode="text-content" /></li>
  </xsl:template>
  
  <xsl:template match="doc:li" mode="nlist">
    <li>
      <xsl:apply-templates />
    </li>
  </xsl:template>

  <xsl:template match="doc:dt" mode="dlist">
    <dt><xsl:apply-templates mode="text-content" /></dt>
  </xsl:template>

  <xsl:template match="doc:dd" mode="dlist">
    <dd><xsl:apply-templates mode="text-content" /></dd>
  </xsl:template>

  <xsl:template match="text()" mode="pre">
    <xsl:copy />
  </xsl:template>

  <xsl:template match="doc:strong" mode="text-content">
    <strong><xsl:apply-templates mode="text-content" /></strong>
  </xsl:template>

  <xsl:template match="doc:em" mode="text-content">
    <em><xsl:apply-templates mode="text-content" /></em>
  </xsl:template>
  
  <xsl:template match="doc:super" mode="text-content">
    <sup><xsl:apply-templates mode="text-content" /></sup>
  </xsl:template>
  
  <xsl:template match="doc:sub" mode="text-content">
    <sub><xsl:apply-templates mode="text-content" /></sub>
  </xsl:template>

  <xsl:template match="doc:link[@target]" mode="text-content">
    <a href="{@url}" target="{@target}"><xsl:apply-templates mode="text-content" /></a>
  </xsl:template>

  <xsl:template match="doc:link" mode="text-content">
    <a href="{@url}"><xsl:apply-templates mode="text-content" /></a>
  </xsl:template>
  
  <xsl:template match="doc:image[@link]">
    <a href="{@link}">
      <img src="{@path}" />
    </a>
  </xsl:template>

  <xsl:template match="doc:image[not(@link)]">
    <img src="{@path}" />
  </xsl:template>
  
  <xsl:template match="doc:underline" mode="text-content">
    <span class="underline"><xsl:apply-templates mode="text-content" /></span>
  </xsl:template>

  <xsl:template match="doc:index">
    <a name="{@name}" />
  </xsl:template>

  <xsl:template match="doc:toc">
    <xsl:copy-of select="./doc:rendered_html/@*|node()" />
  </xsl:template>
  
  <xsl:template match="doc:external_data">
    <xsl:copy-of select="./doc:rendered_html/@*|node()" />
  </xsl:template>
  
  <xsl:template match="doc:code">
    <xsl:copy-of select="./doc:rendered_html/@*|node()" />
  </xsl:template>

  <xsl:template match="doc:source">
    <xsl:copy-of select="./doc:rendered_html/@*|node()" />
  </xsl:template>
  
  <xsl:template match="doc:br" mode="text-content">
    <br />
  </xsl:template>

  <xsl:template match="doc:table">
    <table>
      <xsl:attribute name="class">
        silvatable <xsl:value-of select="@type" />
      </xsl:attribute>
      <xsl:if test="./doc:row_heading">
        <thead>
          <tr valign="top">
            <th colspan="*" class="transparent">
              <xsl:value-of select="./doc:row_heading" />
            </th>
          </tr>
        </thead>
      </xsl:if>
      <tbody>
        <xsl:apply-templates mode="table-contents" />
      </tbody>
    </table>
  </xsl:template>

  <xsl:template match="doc:row_heading" mode="table-contents">
  </xsl:template>
  
  <xsl:template match="doc:row" mode="table-contents">
    <tr>
      <xsl:apply-templates mode="tablerow-contents" />
    </tr>
  </xsl:template>

  <xsl:template match="doc:field" mode="tablerow-contents">
    <td>
      <xsl:apply-templates />
    </td>
  </xsl:template>

</xsl:stylesheet>
