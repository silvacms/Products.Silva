# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from StringIO import StringIO
from lxml import etree
import os
import threading

from five import grok

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.transform.interfaces import IRenderer, IXMLSource


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


class XSLTTransformer(object):

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
        self._error_handler = ErrorHandler()
        # we store stylesheets in a thread-local storage
        self._local = threading.local()

    def stylesheet(self):
        if not hasattr(self._local, 'stylesheet'):
            f = open(self._stylesheet_path)
            parser = etree.XMLParser()
            parser.resolvers.add(ImportResolver(self._import_dir))
            xslt_doc = etree.parse(f, parser)
            f.close()
            self._local.stylesheet = etree.XSLT(xslt_doc)
        return self._local.stylesheet

    def transform(self, obj):
        source_xml = IXMLSource(obj).getXML(external_rendering=True)
        return self.transform_xml(source_xml)

    def transform_xml(self, text):
        style = self.stylesheet()
        doc = etree.parse(StringIO(text))
        result_tree = style(doc)
        result_string = str(result_tree).decode('utf-8')
        doctypestring = '<!DOCTYPE'
        if result_string.startswith(doctypestring):
            result_string = result_string[result_string.find('>')+1:]
        return result_string


class XSLTRendererBase(XSLTTransformer):
    grok.implements(IRenderer)
    grok.baseclass()

    security = ClassSecurityInfo()
    security.declareObjectPublic()
    security.declareProtected("View", "transform_xml")
    security.declareProtected("View", "render")

    render = XSLTTransformer.transform

InitializeClass(XSLTRendererBase)
