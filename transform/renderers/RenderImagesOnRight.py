#!/usr/bin/python

import os
import libxml2, libxslt

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import Acquisition

# Silva
from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.adapters import xmlsource

XSLT_STYLESHEET = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "images_to_the_right.xslt")


class RenderImagesOnRight(Acquisition.Implicit):

    __implements__ = IRenderer

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    security.declareProtected("View", "render")
    def render(self, obj):

        source = xmlsource.getXMLSourceAdapter(obj)
        source_xml = source.getXML()
        xslt_stylesheet = open(XSLT_STYLESHEET).read()
        xslt_stylesheet = xslt_stylesheet % {'url': os.path.dirname(os.path.abspath(__file__))}

        styledoc = libxml2.parseDoc(xslt_stylesheet)
        style = libxslt.parseStylesheetDoc(styledoc)
        doc = libxml2.parseDoc(source_xml)

        result = style.applyStylesheet(doc,{})
        result_as_string = style.saveResultToString(result)

        style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()

        return result_as_string

    security.declareProtected("View", "getName")
    def getName(self):
        return "Images on Right"

InitializeClass(RenderImagesOnRight)
