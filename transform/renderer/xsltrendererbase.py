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

class RenderError(Exception):
    """I'm raised when something went wrong during the rendering"""
    pass

class ErrorHandler:
    def __init__(self):
        self._error_text = ""

    def callback(self, ctx, s):
        self._error_text += s

    def getErrorText(self):
        return self._error_text

class XSLTRendererBase(Acquisition.Implicit):

    __implements__ = IRenderer

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self):
        self._name = ''
        self._stylesheet_path = None
        self._stylesheet = None
        self._error_handler = ErrorHandler()
        libxml2.registerErrorHandler(self._error_handler.callback, None)

    def stylesheet(self):
        if self._stylesheet is None:
            xslt_stylesheet = open(self._stylesheet_path).read()
            xslt_stylesheet = xslt_stylesheet % {'url': os.path.dirname(os.path.abspath(__file__))}
            try:
                styledoc = libxml2.parseDoc(xslt_stylesheet)
                self._stylesheet = libxslt.parseStylesheetDoc(styledoc)
            except libxml2.parserError, err:
                raise RenderError(
                    self._error_handler.getErrorText() or str(err))

        if self._stylesheet is None:
            raise RenderError(self._error_handler.getErrorText())

        return self._stylesheet

    security.declareProtected("View", "render")
    def render(self, obj):
        source = xmlsource.getXMLSourceAdapter(obj)
        source_xml = source.getXML()

        style = self.stylesheet()
        try:
            doc = libxml2.parseDoc(source_xml)
            result = style.applyStylesheet(doc, {})
        except libxml2.parserError, err:
            raise RenderError(
                self._error_handler.getErrorText() or str(err))

        if not result:
            raise RenderError(self._error_handler.getErrorText())
        try:
            result_string = style.saveResultToString(result)
        except libxml2.parserError:
            raise RenderError(self._error_handler.getErrorText())

        doc.freeDoc()
        result.freeDoc()

        return result_string

    security.declareProtected("View", "getName")
    def getName(self):
        return self._name

InitializeClass(XSLTRendererBase)
