# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.79.2.4 $
# Zope

from StringIO import StringIO

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass

# Silva interfaces
from IVersionedContent import IVersionedContent, ICatalogedVersionedContent
from IVersion import IVersion, ICatalogedVersion

# Silva
import SilvaPermissions
from VersionedContent import CatalogedVersionedContent
from helpers import add_and_edit, translateCdata, getNewId
from Version import CatalogedVersion

# For XML-Conversions for editors
from transform.Transformer import EditorTransformer
from transform.base import Context

from Products.Silva.ImporterRegistry import importer_registry, xml_import_helper, get_xml_id, get_xml_title
from Products.Silva.Metadata import export_metadata
from Products.ParsedXML.ExtraDOM import writeStream
from Products.ParsedXML.ParsedXML import createDOMDocument
from Products.ParsedXML.PrettyPrinter import _translateCdata
from Products.ParsedXML.ParsedXML import ParsedXML

icon="www/silvadoc.gif"

class Document(CatalogedVersionedContent):
    """A Document is the basic unit of information in Silva. A document
        can -  much like word processor documents - contain text,
        lists, tables, headers, subheads, images, etc. Documents can have
        two (accessible) versions, one online for the public, another in
        process (editable or approved).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Document"

    __implements__ = IVersionedContent, ICatalogedVersionedContent

    # A hackish way, to get a Silva tab in between the standard ZMI tabs
    inherited_manage_options = CatalogedVersionedContent.manage_options
    manage_options=(
        (inherited_manage_options[0],)+
        ({'label':'Silva /edit...', 'action':'edit'},)+
        inherited_manage_options[1:]
        )

    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, datasource or toc.
        """
        non_cacheable_objects = ['toc', 'code', 'externaldata']
        is_cacheable = 1 
    
        viewable = self.get_viewable()

        if viewable is None:
            return 0

        # it should suffice to test the children of the root element only,
        # since currently the only non-cacheable elements are root elements
        for node in viewable.content.documentElement.childNodes:
            if node.nodeName in non_cacheable_objects:
                is_cacheable = 0
                break
        
        return is_cacheable
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f

        if context.last_version == 1:
            version_id = self.get_next_version()
            if version_id is None:
                version_id = self.get_public_version()
        else:
            version_id = self.get_public_version()

        if version_id is None:
            return
        f.write('<silva_document id="%s">' % self.id) 
        version = getattr(self, version_id)
        version.to_xml(context)        
        f.write('</silva_document>')


    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 
                              'editor_storage')
    def editor_storage(self, string=None, editor='eopro3_0', encoding='UTF-8'):
        """provide xml/xhtml/html (GET requests) and (heuristic) 
           back-transforming to xml/xhtml/html (POST requests)
        """
        transformer = EditorTransformer(editor=editor)

        if string is None:
            ctx = Context(f=StringIO(), last_version=1, url=self.absolute_url())
            self.to_xml(ctx)
            htmlnode = transformer.to_target(sourceobj=ctx.f.getvalue(), context=ctx)
            if encoding:
                return htmlnode.asBytes(encoding=encoding)
            else:
                return unicode(htmlnode.asBytes('utf8'),'utf8')
        else:
            version = self.get_editable()
            if version is None:
                raise "Hey, no version to store to!"
            
            ctx = Context(url=self.absolute_url())
            silvanode = transformer.to_source(targetobj=string, context=ctx)[0]
            title = silvanode.find_one('title').extract_text()
            docnode = silvanode.find_one('doc')
            content = docnode.asBytes(encoding="UTF8")
            version.content.manage_edit(content)  # needs utf8-encoded string
            self.set_title(title)         # needs unicode

            # brute force: invalidate all widget caches for this session
            try:
                del self.REQUEST.SESSION['xmlwidgets_service_editor']
            except AttributeError: pass
            except KeyError: pass

    security.declarePrivate('get_indexables')
    def get_indexables(self):
        version = self.get_viewable()
        if version is None:
            return []
        return [version]

    def manage_beforeDelete(self, item, container):
        Document.inheritedAttribute('manage_beforeDelete')(self, item, container)
        # Does the widget cache needs be cleared for all versions - I think so...
        for version in self._get_indexable_versions():
            self.service_editor.clearCache(version.content)

InitializeClass(Document)

class DocumentVersion(CatalogedVersion):
    """Silva Document version.
    """
    meta_type = "Silva Document Version"
    __implements__ = IVersion, ICatalogedVersion

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Edit',       'action':'manage_main'},
        ) + CatalogedVersion.manage_options
    
    def __init__(self, id, title):
        DocumentVersion.inheritedAttribute('__init__')(self, id, title)
        self.content = ParsedXML('content', '<doc></doc>')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile('www/documentVersionEdit', globals())
        
    def to_xml(self, context):
        f = context.f
        f.write('<title>%s</title>' % translateCdata(self.get_title()))
        self.content.documentElement.writeStream(f)
        export_metadata(self, context)

    def manage_afterClone(self, item):
        # if we're a copy, clear cache
        # XXX should be part of workflow system
        self.service_editor.clearCache(self.content)
        
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'fulltext')
    def fulltext(self):
        """Return the content of this object without any xml

        Don't do this in case of an unapproved document though.
        """
        if self.version_status() == 'unapproved':
            return ''
        # include title and text body
        return [self.get_title(), self._flattenxml(self.content_xml())]
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'content_xml')
    def content_xml(self):
        """Returns the documentElement of the content's XML
        """
        s = StringIO()
        self.content.documentElement.writeStream(s)
        value = s.getvalue()
        s.close()
        return value

    def _flattenxml(self, xmlinput):
        """Cuts out all the XML-tags, helper for fulltext (for content-objects)
        """
        # XXX this need to be fixed by using ZCTextIndex or the like
        return xmlinput
        
InitializeClass(DocumentVersion)

manage_addDocumentForm = PageTemplateFile("www/documentAdd", globals(),
                                          __name__='manage_addDocumentForm')

def manage_addDocument(self, id, title, REQUEST=None):
    """Add a Document."""
    if not self.is_id_valid(id):
        return
    object = Document(id)
    self._setObject(id, object)
    object = getattr(self, id)
    object.manage_addProduct['Silva'].manage_addDocumentVersion('0', title)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addDocumentVersionForm = PageTemplateFile(
    "www/documentVersionAdd",
    globals(),
    __name__='manage_addDocumentVersionForm')

def manage_addDocumentVersion(self, id, title, REQUEST=None):
    """Add a Document version to the Silva-instance."""
    version = DocumentVersion(id, title)
    self._setObject(id, version)
    
    version = self._getOb(id)
    version.set_title(title)

    add_and_edit(self, id, REQUEST)
    return ''

def xml_import_handler(object, node):
    id = get_xml_id(node)
    title = get_xml_title(node)
    
    used_ids = object.objectIds()
    while id in used_ids:
        id = getNewId(id)
        
    object.manage_addProduct['Silva'].manage_addDocument(id, title)
    
    newdoc = getattr(object, id)
    newdoc.sec_update_last_author_info()
    
    for child in node.childNodes:
        if child.nodeName == u'doc':
            version = getattr(newdoc, '0')
            childxml = writeStream(child).getvalue().encode('utf8')
            version.content.manage_edit(childxml) # expects utf8
        elif hasattr(newdoc, 'set_%s' % child.nodeName.encode('utf8')) \
                and child.nodeValue:
            getattr(newdoc, 'set_%s' % child.nodeName.encode('utf8'))(
                child.nodeValue.encode('utf8'))

    return newdoc
