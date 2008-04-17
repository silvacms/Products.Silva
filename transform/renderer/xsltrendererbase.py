import os
import urllib
from lxml import etree
from StringIO import StringIO

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import Acquisition

# Silva
from Products.Silva.transform.interfaces import IRenderer
from Products.Silva.adapters import xmlsource

class ErrorHandler:
    def __init__(self):
        self._error_text = ""

    def callback(self, ctx, s):
        self._error_text += s

    def getErrorText(self):
        return self._error_text

class XSLTRendererBase(Acquisition.Implicit):

    implements(IRenderer)

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self, path, file_context):
        """XSLT-based renderer.

        path - the relative path to use to the XSLT stylesheet
        file_context - the directory or file in the directory to look in.
        Typically __file__ is passed to look in the module's context.
        """
        path_context = os.path.dirname(os.path.abspath(file_context))
        if os.path.isdir(path_context) and not path_context.endswith('/'):
            path_context += '/'
        self._stylesheet_path = os.path.join(path_context, path)
        self._stylesheet_dir = path_context
        self._stylesheet = None
        self._error_handler = ErrorHandler()

    def stylesheet(self):
        if self._stylesheet is None:
            f = open(self._stylesheet_path)
            xslt_doc = etree.parse(f)
            f.close()
            self._stylesheet = etree.XSLT(xslt_doc)
    
        return self._stylesheet

    security.declareProtected("View", "render")
    def render(self, obj):
        source = xmlsource.getXMLSourceAdapter(obj)
        source_xml = source.getXML()

        style = self.stylesheet()
        doc = etree.parse(StringIO(source_xml))
        result_tree = style(doc)
        result_string = str(result_tree)
        doctypestring = '<!DOCTYPE'
        if result_string.startswith(doctypestring):
            result_string = result_string[result_string.find('>')+1:]
            
        return result_string

InitializeClass(XSLTRendererBase)
