# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
from lxml import etree
from StringIO import StringIO

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

# Silva
from Products.Silva.transform.interfaces import IRenderer, IXMLSource
from Products.Silva.adapters import xmlsource
from silva.core import conf as silvaconf

class ErrorHandler(object):
    def __init__(self):
        self._error_text = ""

    def callback(self, ctx, s):
        self._error_text += s

    def getErrorText(self):
        return self._error_text

class ImportResolver(etree.Resolver):
    def __init__(self, import_dir):
        self.import_dir = import_dir
        
    def resolve(self, url, id, context):
        if url.startswith("silvabase:"):
            return self.resolve_filename(self.import_dir + url[10:], context)
    
class XSLTRendererBase(object):

    implements(IRenderer)

    security = ClassSecurityInfo()
    security.declareObjectPublic()

    silvaconf.baseclass()

    def __init__(self, path, file_context, import_context=__file__):
        """XSLT-based renderer.

        path - the relative path to use to the XSLT stylesheet

        file_context - the directory or file in the directory to look
                       in. Typically __file__ is passed to look in the
                       module's context.

        import_context - usually this directory: the place to import
                         doc_elements.xslt from.
        """
        path_context = os.path.dirname(os.path.abspath(file_context))
        if os.path.isdir(path_context) and not path_context.endswith('/'):
            path_context += '/'
        import_dir = os.path.dirname(os.path.abspath(import_context))
        if os.path.isdir(import_dir) and not import_dir.endswith('/'):
            import_dir += '/'
        self._stylesheet_path = os.path.join(path_context, path)
        self._stylesheet_dir = path_context
        self._import_dir = import_dir
        self._stylesheet = None
        self._error_handler = ErrorHandler()

    def stylesheet(self):
        if self._stylesheet is None:
            f = open(self._stylesheet_path)
            parser = etree.XMLParser()
            parser.resolvers.add(ImportResolver(self._import_dir))
            xslt_doc = etree.parse(f, parser)
            f.close()
            self._stylesheet = etree.XSLT(xslt_doc)
        return self._stylesheet

    security.declareProtected("View", "render")
    def render(self, obj):
        source_xml = IXMLSource(obj).getXML(external_rendering=True)

        style = self.stylesheet()
        doc = etree.parse(StringIO(source_xml))
        result_tree = style(doc)
        result_string = str(result_tree)
        doctypestring = '<!DOCTYPE'
        if result_string.startswith(doctypestring):
            result_string = result_string[result_string.find('>')+1:]
            
        return result_string

    security.declareProtected("View", "render")
    def render_snippet(self, text):
        style = self.stylesheet()
        doc = etree.parse(StringIO(text))
        result_tree = style(doc)
        result_string = str(result_tree)
        doctypestring = '<!DOCTYPE'
        if result_string.startswith(doctypestring):
            result_string = result_string[result_string.find('>')+1:]
        return result_string

InitializeClass(XSLTRendererBase)
