<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0">

<xsl:strip-space elements="*" />
<xsl:preserve-space elements="heading p pre li em strong super sub underline link" />

<xsl:template match="/">
<table>
<tr>
  <td>
    <xsl:apply-templates mode="text" />
  </td>
  <td>
    <xsl:apply-templates mode="images" />
  </td>
</tr>
</table>
</xsl:template>

<xsl:template match="heading[@type='normal']" mode="text">
  <h3 class="heading"><xsl:apply-templates mode="text-content" /></h3>
</xsl:template>

<xsl:template match="heading[@type='sub']" mode="text">
  <h4 class="heading"><xsl:apply-templates mode="text-content" /></h4>
</xsl:template>

<xsl:template match="heading[@type='subsub']" mode="text">
  <h3 class="heading"><xsl:apply-templates mode="text-content" /></h3>
</xsl:template>

<xsl:template match="heading[@type='paragraph']" mode="text">
  <h6 class="heading"><xsl:apply-templates mode="text-content" /></h6>
</xsl:template>

<xsl:template match="heading[@type='subparagraph']" mode="text">
  <h6 class="minor"><xsl:apply-templates mode="text-content" /></h6>
</xsl:template>

<xsl:template match="p" mode="text">
<p class="{@type}"><xsl:apply-templates mode="text-content" /></p>
</xsl:template>

<xsl:template match="list[@type='disc']" mode="text">
<ul class="disc">
  <xsl:apply-templates mode="list" />
</ul>
</xsl:template>

<xsl:template match="list[@type='square']" mode="text">
<ul class="square">
  <xsl:apply-templates mode="list" />
</ul>
</xsl:template>

<xsl:template match="list[@type='circle']" mode="text">
<ul class="circle">
  <xsl:apply-templates mode="list" />
</ul>
</xsl:template>

<xsl:template match="list[@type='1']" mode="text">
<ol class="decimal">
  <xsl:apply-templates mode="list" />
</ol>
</xsl:template>

<xsl:template match="list[@type='I']" mode="text">
<ol class="upper-roman">
  <xsl:apply-templates mode="list" />
</ol>
</xsl:template>

<xsl:template match="list[@type='i']" mode="text">
<ol class="lower-roman">
  <xsl:apply-templates mode="list" />
</ol>
</xsl:template>

<xsl:template match="list[@type='A']" mode="text">
<ol class="upper-alpha">
  <xsl:apply-templates mode="list" />
</ol>
</xsl:template>

<xsl:template match="list[@type='a']" mode="text">
<ol class="lower-alpha">
  <xsl:apply-templates mode="list" />
</ol>
</xsl:template>

<!-- need IE support? -->
<xsl:template match="list[@type='none']" mode="text">
<ul class="nobullet">
  <xsl:apply-templates mode="list" />
</ul>
</xsl:template>

<xsl:template match="dlist" mode="text">
<dl class="dl">
  <xsl:if test="@type='compact'">
    <xsl:attribute name="compact">compact</xsl:attribute>
  </xsl:if>
  <xsl:apply-templates mode="dlist" />
</dl>
</xsl:template>

<xsl:template match="pre" mode="text">
<pre class="pre"><xsl:apply-templates mode="pre" /></pre>
</xsl:template>

<xsl:template match="li" mode="list">
<li><xsl:apply-templates mode="text-content" /></li>
</xsl:template>

<xsl:template match="dt" mode="dlist">
<dt><xsl:apply-templates mode="text-content" /></dt>
</xsl:template>

<xsl:template match="dd" mode="dlist">
<dd><xsl:apply-templates mode="text-content" /></dd>
</xsl:template>

<xsl:template match="text()" mode="pre">
<xsl:copy />
</xsl:template>

<xsl:template match="strong" mode="text-content">
<strong><xsl:apply-templates mode="text-content" /></strong>
</xsl:template>

<xsl:template match="em" mode="text-content">
<em><xsl:apply-templates mode="text-content" /></em>
</xsl:template>

<xsl:template match="super" mode="text-content">
<super>xsl:apply-templates mode="text-content" /></super>
</xsl:template>

<xsl:template match="text()" mode="images">
</xsl:template>

<xsl:template match="image" mode="images">
<img src="{@path}" /><br />
</xsl:template>

</xsl:stylesheet>
