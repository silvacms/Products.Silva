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
  For your own renderers for Silva Documents, import this stylesheet and
  override where necessary. It is better not to modify this stylesheet
  directly. See images_to_the_right.xslt for a documented example.
  -->

  <xsl:template match="doc:heading[@type='normal']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <h3 class="heading"><xsl:apply-templates mode="text-content" /></h3>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='sub']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <h4 class="heading"><xsl:apply-templates mode="text-content" /></h4>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subsub']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <h5 class="heading"><xsl:apply-templates mode="text-content" /></h5>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='paragraph']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <h6 class="heading"><xsl:apply-templates mode="text-content" /></h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:heading[@type='subparagraph']">
    <xsl:choose>
      <xsl:when test="not(text()[normalize-space(.)] | *)" />
      <xsl:otherwise>
        <h6 class="minor"><xsl:apply-templates mode="text-content" /></h6>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:p[@type]">
    <xsl:choose>
      <xsl:when test="./@type='normal'">
        <p class="p"><xsl:apply-templates mode="text-content" /></p>
      </xsl:when>
      <xsl:otherwise>
        <p class="{@type}"><xsl:apply-templates mode="text-content" /></p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:p[not(@type)]">
    <p class="p"><xsl:apply-templates mode="text-content" /></p>
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

  <xsl:template match="doc:nlist[@type='1']">
    <ol class="decimal">
      <xsl:apply-templates mode="nlist" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:nlist[@type='I']">
    <ol class="upper-roman">
      <xsl:apply-templates mode="nlist" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:nlist[@type='i']">
    <ol class="lower-roman">
      <xsl:apply-templates mode="nlist" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:nlist[@type='A']">
    <ol class="upper-alpha">
      <xsl:apply-templates mode="nlist" />
    </ol>
  </xsl:template>

  <xsl:template match="doc:nlist[@type='a']">
    <ol class="lower-alpha">
      <xsl:apply-templates mode="nlist" />
    </ol>
  </xsl:template>

  <!-- need IE support? -->
  <xsl:template match="doc:nlist[@type='none']">
    <ul class="nobullet">
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

  <xsl:template match="doc:strike" mode="text-content">
    <strike><xsl:apply-templates mode="text-content" /></strike>
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

  <xsl:template match="doc:link" mode="text-content">
    <a href="{@href|@url}" title="{@title}">
      <xsl:if test="@class">
        <xsl:attribute name="class">
          <xsl:value-of select="@class" />
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="@target">
        <xsl:attribute name="target">
          <xsl:value-of select="@target" />
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates mode="text-content" />
    </a>
  </xsl:template>

  <xsl:template match="doc:abbr" mode="text-content">
    <abbr title="{@title}">
      <xsl:copy-of select="./node()" />
    </abbr>
  </xsl:template>

  <xsl:template match="doc:acronym" mode="text-content">
    <acronym title="{@title}">
      <xsl:copy-of select="./node()" />
    </acronym>
  </xsl:template>

  <xsl:template match="doc:link">
    <xsl:choose>
      <xsl:when test="count(*) = 1 and count(doc:image) = 1">
        <xsl:variable name="image" select="doc:image" />
        <xsl:choose>
          <xsl:when test="starts-with($image/@alignment, 'image-')">
            <div class="{$image/@alignment}">
              <a href="{@href|@url}" title="{@title}" target="{@target}">
                <xsl:apply-templates mode="image-content" />
              </a>
            </div>
          </xsl:when>
          <xsl:otherwise>
            <a href="{@href|@url}" title="{@title}" target="{@target}">
              <xsl:apply-templates mode="image-content" />
            </a>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <p class="error">Error: junk within link</p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:image">
    <xsl:choose>
      <xsl:when test="starts-with(@alignment, 'image-')">
        <div class="{@alignment}">
          <xsl:apply-templates select="." mode="image-content" />
        </div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="." mode="image-content" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:image" mode="image-content">
    <img src="{@rewritten_path}" alt="{@title}" class="{@alignment}">
      <xsl:if test="@width">
        <xsl:attribute name="width">
          <xsl:value-of select="@width" />
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="@height">
        <xsl:attribute name="height">
          <xsl:value-of select="@height" />
        </xsl:attribute>
      </xsl:if>
    </img>
  </xsl:template>

  <xsl:template match="doc:underline" mode="text-content">
    <span class="underline"><xsl:apply-templates mode="text-content" /></span>
  </xsl:template>

  <xsl:template match="doc:index" mode="text-content">
    <a class="index-element" id="{@name}" />
  </xsl:template>

  <xsl:template match="doc:code">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="doc:source">
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="*" mode="copy">
    <xsl:element name="{name()}">
      <xsl:apply-templates select="node()|@*" mode="copy"/>
    </xsl:element>
  </xsl:template>
  <xsl:template match="@*" mode="copy">
    <xsl:copy/>
  </xsl:template>

  <xsl:template match="doc:rendered_html">
    <xsl:apply-templates mode="copy" />
  </xsl:template>

  <xsl:template match="doc:parameter" />

  <xsl:template match="doc:br" mode="text-content">
    <br />
  </xsl:template>

  <xsl:template match="doc:table">
    <!-- only render table if it has child nodes (not empty) -->
    <xsl:if test="*">
      <table class="silvatable {@type}" cellspacing="0" cellpadding="3">
        <xsl:apply-templates mode="table-contents" />
      </table>
    </xsl:if>
  </xsl:template>

  <xsl:template match="doc:row_heading" mode="table-contents">
    <!-- this is for backward compatibility (Silva 2.3) -->
    <tr>
      <th colspan="{@colspan}">
        <xsl:apply-templates mode="field-contents" />
      </th>
    </tr>
  </xsl:template>

  <xsl:template match="doc:row" mode="table-contents">
    <tr class="{@class}">
      <xsl:apply-templates mode="tablerow-contents" />
    </tr>
  </xsl:template>

  <xsl:template match="doc:col" mode="table-contents">
    <col width="{@width}" />
  </xsl:template>

  <xsl:template match="doc:field" mode="tablerow-contents">
   <xsl:choose>
      <xsl:when test="@fieldtype='th'">
     <xsl:element name="th">
      <xsl:if test="@colspan">
       <xsl:attribute name="colspan">
         <xsl:value-of select="@colspan" />
       </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="." mode="field-contents" />
     </xsl:element>
    </xsl:when>
    <xsl:otherwise>
     <xsl:element name="td">
      <xsl:if test="@colspan">
       <xsl:attribute name="colspan">
         <xsl:value-of select="@colspan" />
       </xsl:attribute>
      </xsl:if>
      <xsl:if test="@class">
       <xsl:attribute name="class">
         <xsl:value-of select="@class" />
       </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates select="." mode="field-contents" />
     </xsl:element>
    </xsl:otherwise>
   </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:field" mode="field-contents">
    <!-- IE doesn't like empty table cells, insert a nbsp if there are
      no child elements -->
    <xsl:choose>
      <xsl:when test="count(*) = 1 and count(doc:p) = 1">
        <xsl:apply-templates mode="remove-single-p" />
      </xsl:when>
      <xsl:when test="count(*) = 0">&#160;</xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="doc:p" mode="remove-single-p">
    <xsl:apply-templates mode="text-content" />
  </xsl:template>

</xsl:stylesheet>
