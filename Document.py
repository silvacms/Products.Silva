# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.69 $
# Zope
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

    def __init__(self, id, title):
        Document.inheritedAttribute('__init__')(self, id, title)

        self._metadata = {
            'subject' : '',
            'description' : ''
            }

        self._automatic_metadata = {
            'creator' : '',
            'creation_date' : None,
            'modification_data' : None,
            'author' : '',
            'chief_author' : '',
            'manager' : '',
            'location' : '',
            'publisher' : ''
            }

#    def manage_afterClone(self, obj):
#        """We were copied, make sure we're not public.
#        """
#        # if we don't have any public version we're fine
#        if not self.get_public_version():
#            return
#        # close any public version
#        self.close_version()

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Set the title.
        """
        if self.is_default():
            # set the nearest container's title
            self.get_container().set_title(title)
        else:
            # set title of this document
            self._title = title

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_metadata')
    def set_metadata(self, name, value):
        """Set meta data.
        """
        if name == 'document_title':
            self.set_title(value)
            return
        # FIXME perhaps should put this in again for security, but
        # leaving it out makes it nice for extensibility
        #if not self._metadata.has_key(name):
        #    return
        self._metadata[name] = value
        self._metadata = self._metadata

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title')
    def get_title(self):
        """Get title. If we're the default document,
        we get title from our containing folder (or publication, etc).
        """
        if self.is_default():
            # get the nearest container's title
            return self.get_container().get_title()
        else:
            return self._title

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_metadata')
    def get_metadata(self, name):
        """Get meta data.
        """
        if name == 'document_title':
            return self.get_title()
        return self._metadata.get(name, None)

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
        version = getattr(self, version_id)
        f.write('<silva_document id="%s">' % self.id)
        f.write('<title>%s</title>' % translateCdata(self.get_title()))
        #for key, value in self._metadata.items():
        #    f.write('<%s>%s</%s>' % (key, translateCdata(value), key))
        
        version.content.documentElement.writeStream(f)
        export_metadata(version, context)
        
        f.write('</silva_document>')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'store_xml')
    def store_xml(self, xml):
        """Store the Document from the xml-string in this object.

           the xml string is usually utf-8 encoded. Make sure
           that the "encoding" in any xml-processing instruction
           really matches the encoding of the string.
           Weird Errors can occur if they differ!

        """
        version = self.get_editable()
        if version is None:
            # XXX should put in nicer exceptions (or just return)
            raise "Hey, no version to edit!"

        dom = createDOMDocument(xml)

        title = content = None
        # hackish way to do this..

        for node in dom.documentElement.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                if node.nodeName == 'title':
                    title = node.childNodes[0].nodeValue
                if node.nodeName == 'doc':
                    content = writeStream(node).getvalue().encode('utf8')

        if title is None or content is None:
            # XXX should put in nicer exceptions (or just return)
            raise "Hey, title or content was empty! %s %s" % (repr(title), repr(content))

        version.content.manage_edit(content)  # needs utf8-encoded string
        self.set_title(title)         # needs unicode

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 
                              'editor_storage')
    def editor_storage(self, string=None, editor='eopro3_0', encoding='UTF-8'):
        """provide xml/xhtml/html (GET requests) and (heuristic) 
           back-transforming to xml/xhtml/html (POST requests)
        """
        from cStringIO import StringIO
        transformer = EditorTransformer(editor=editor)

        if string is None:
            ctx = Context(f=StringIO(), last_version=1, url=self.absolute_url())
            self.to_xml(ctx)
            htmlnode = transformer.to_target(sourceobj=ctx.f.getvalue(), context=ctx)
            return htmlnode.asBytes(encoding=encoding)
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

    security.declarePrivate('get_indexables')
    def get_indexables(self):
        version = self.get_viewable()
        if version is None:
            return []
        return [version]

InitializeClass(Document)

class DocumentVersion(CatalogedVersion):
    """Silva Document version.
    """
    meta_type = "Silva Document Version"
    __implements__ = IVersion, ICatalogedVersion

InitializeClass(DocumentVersion)

manage_addDocumentForm = PageTemplateFile("www/documentAdd", globals(),
                                          __name__='manage_addDocumentForm')

def manage_addDocument(self, id, title, REQUEST=None):
    """Add a Document."""
    if not self.is_id_valid(id):
        return
    object = Document(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    object.manage_addProduct['Silva'].manage_addDocumentVersion('0')
    object.create_version('0', None, None)
    getattr(object, '0').index_object()
    add_and_edit(self, id, REQUEST)
    return ''

manage_addDocumentVersionForm = PageTemplateFile(
    "www/documentVersionAdd",
    globals(),
    __name__='manage_addDocumentVersionForm')

def manage_addDocumentVersion(self, id, title=None, REQUEST=None):
    """Add a Document version to the Silva-instance."""
    object = DocumentVersion(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''

def xml_import_handler(object, node):
    print object
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
