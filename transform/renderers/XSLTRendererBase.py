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

class XSLTRendererBase(Acquisition.Implicit):

    __implements__ = IRenderer

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self):
        self._name = ''
        self._stylesheet_path = None
        self._stylesheet = None
        
    def stylesheet(self):
        if self._stylesheet is None:
            xslt_stylesheet = open(self._stylesheet_path).read()
            xslt_stylesheet = xslt_stylesheet % {'url': os.path.dirname(os.path.abspath(__file__))}
            styledoc = libxml2.parseDoc(xslt_stylesheet)
            self._stylesheet = libxslt.parseStylesheetDoc(styledoc)
        return self._stylesheet
    
    security.declareProtected("View", "render")
    def render(self, obj):

        source = xmlsource.getXMLSourceAdapter(obj)
        source_xml = source.getXML()

        style = self.stylesheet()
        doc = libxml2.parseDoc(source_xml)
        
        print repr(style)
        result = style.applyStylesheet(doc,{})
        result_as_string = style.saveResultToString(result)

        style.freeStylesheet()
        doc.freeDoc()
        result.freeDoc()

        return result_as_string

    security.declareProtected("View", "getName")
    def getName(self):
        return self._name

InitializeClass(XSLTRendererBase)
