# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.56 $
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
from StringIO import StringIO

# Silva interfaces
from IVersionedContent import IVersionedContent

# Silva
import SilvaPermissions
from VersionedContent import VersionedContent
from helpers import add_and_edit, translateCdata, getNewId

# For XML-Conversions for editors
from transform.Transformer import EditorTransformer

from Products.Silva.ImporterRegistry import importer_registry, xml_import_helper, get_xml_id, get_xml_title
from Products.ParsedXML.ExtraDOM import writeStream
from Products.ParsedXML.ParsedXML import createDOMDocument
from Products.ParsedXML.PrettyPrinter import _translateCdata

icon="www/silvadoc.gif"

class Document(VersionedContent):
    """A Document is the basic unit of information in Silva. A document
        can -  much like word processor documents - contain text,
        lists, tables, headers, subheads, images, etc. Documents can have
        two (accessible) versions, one online for the public, another in
        process (editable or approved).
    """
    security = ClassSecurityInfo()

    meta_type = "Silva Document"

    __implements__ = IVersionedContent

    # A hackish way, to get a Silva tab in between the standard ZMI tabs
    inherited_manage_options = VersionedContent.manage_options
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
        # XXX hack, should check for dynamic content in public view
        return 1
        
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
        version.documentElement.writeStream(f)
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

        version.manage_edit(content)  # needs utf8-encoded string
        self.set_title(title)         # needs unicode

    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 
                              'editor_storage')
    def editor_storage(self, string=None, editor='eopro2_11', encoding='UTF-8'):
        """provide xml/xhtml/html (GET requests) and (heuristic) 
           back-transforming to xml/xhtml/html (POST requests)
        """
        transformer = EditorTransformer(editor=editor)

        if string is None:
            string = self.get_xml(last_version=1, with_sub_publications=0)
            htmlnode = transformer.to_target(sourceobj=string)
            return htmlnode.asBytes(encoding=encoding)
        else:
            version = self.get_editable()
            if version is None:
                raise "Hey, no version to store to!"
            conv_context = {'id': self.id,
                            'title': self.get_title()}

            silvanode = transformer.to_source(targetobj=string,
                                              context=conv_context
                                              )[0]
            title = silvanode.find('title')[0].content.asBytes(encoding='utf8')
            title = unicode(title, 'utf8')
            docnode = silvanode.find('doc')[0]
            content = docnode.asBytes(encoding="UTF8")
            version.manage_edit(content)  # needs utf8-encoded string
            self.set_title(title)         # needs unicode

#    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
#                              'to_folder')
#    def to_folder(self):
#        """Convert this document to folder in same place.
#        """
#        # get id of document; this will be the id of the folder
#        id = self.id
#        # we will rename ourselves to a temporary id
#        temp_id = 'silva_temp_%s' % id
#        # get parent folder
#        parent = self.get_container()
#        # rename doc so we can create folder with the same name
#        parent.manage_renameObject(id, temp_id)
#        # create Silva Folder to hold self
#        parent.manage_addProduct['Silva'].managre_addFolder(id, self.title(), 0)
#        # get folder
#        folder = getattr(parent, id)
#        # now add self to folder
#        cb = parent.manage_cutObjects([temp_id])
#        folder.manage_pasteObjects(cb_copy_data=cb)
#        # rename doc from temp_id to 'doc'
#        folder.manage_renameObject(temp_id, 'doc')
#        return folder

 #   def action_paste(self, REQUEST):
 #       """Convert this to Folder and paste objects on clipboard.
 #       """
 #       # convert myself to a folder
 #       folder = self.to_folder()
 #       # paste stuff into the folder
 #       folder.action_paste(REQUEST)

    security.declarePrivate('get_indexables')
    def get_indexables(self):
        version = self.get_viewable()
        if version is None:
            return []
        return [version]

InitializeClass(Document)

manage_addDocumentForm = PageTemplateFile("www/documentAdd", globals(),
                                          __name__='manage_addDocumentForm')

def manage_addDocument(self, id, title, REQUEST=None):
    """Add a Document."""
    if not self.is_id_valid(id):
        return
    object = Document(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add empty ParsedXML object
    str = """<doc></doc>"""
    object.manage_addProduct['ParsedXML'].manage_addParsedXML('0', '', str)
    object.create_version('0', None, None)
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
            version.manage_edit(childxml) # expects utf8
        elif hasattr(newdoc, 'set_%s' % child.nodeName.encode('cp1252')) \
                and child.nodeValue:
            getattr(newdoc, 'set_%s' % child.nodeName.encode('cp1252'))(
                child.nodeValue.encode('utf-8'))

            
