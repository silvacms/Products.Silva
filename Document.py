# Zope
from OFS import Folder, ObjectManager, SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
import DateTime
# Silva
from ViewRegistry import ViewAttribute
from TocSupport import TocSupport
from Versioning import Versioning
import ForgivingParser
# misc
from helpers import add_and_edit
from cgi import escape

class Document(TocSupport, Folder.Folder, Versioning):
    """Silva Document.
    """
    meta_type = "Silva Document"

    security = ClassSecurityInfo()
   
    # allow edit view on this object
    edit = ViewAttribute('edit')
 
    manage_options = (
        ( {'label':'Edit', 'action':'manage_editForm'},
          {'label':'Preview', 'action':'manage_previewForm'},
          {'label':'Contents', 'action':'manage_main'},
          {'label':'Undo', 'action':'manage_undoForm'},
          {'label':'Export', 'action':'manage_exportForm'},    
          {'label':'Metadata', 'action':'manage_metadataForm'},
          {'label':'Status', 'action':'manage_statusForm'},
          {'label':'Exits', 'action':'manage_exitsForm'})
        )
    
    manage_editForm = PageTemplateFile('www/documentEdit', globals(),
                                       __name__='manage_main')
    manage_previewForm = PageTemplateFile('www/documentPreview', globals(),
                                          __name__='manage_previewForm')
    manage_undoForm = PageTemplateFile('www/dummy', globals(),
                                       __name__='manage_undoForm')
    manage_exportForm = PageTemplateFile('www/dummy', globals(),
                                         __name__='manage_exportForm')
    manage_metadataForm = PageTemplateFile('www/dummy', globals(),
                                           __name__='manage_metadataForm')
    manage_statusForm = PageTemplateFile('www/dummy', globals(),
                                         __name__='manage_statusForm')
    manage_exitsForm = PageTemplateFile('www/dummy', globals(),
                                       __name__='manage_exitsForm')
    def __init__(self, id, title):
        self.id = id
        self._title = title
        self._version_count = 1
        self._creation_datetime = DateTime.DateTime()

        self._metadata = {
            'document_title' : title,
            'subject' : '',
            'description' : '',
            'expires_flag': 0,
            'audience' : None,
            'language': 'Dutch'
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
        
    def __repr__(self):
        return "<Silva Document instance at %s>" % self.id

    def title(self):
        """Get title. If we're 'doc', we get title from our folder.
        """
        if self.id == 'doc':
            folder = self.get_folder()
            if folder.meta_type in ['Silva Folder', 'Silva Root']:
                return folder.title()
            else:
                return "(Default)"
        elif self.id != '': 
            return self._title
        else:
            return "(Untitled)"

    def set_title(self, title):
        """Set the title.
        """
        self._title = title

    def get_creation_datetime(self):
        """Get document creation date.
        """
        if hasattr(self, '_creation_datetime'):
            return self._creation_datetime
        else:
            # hack
            return DateTime.DateTime(2002, 1, 1, 12,  0)
        
    def get_modification_datetime(self):
        """Get document modification date.
        """
        version = self.get_next_version() or get_public_version()
        doc = getattr(self, version)
        return doc.bobobase_modification_datetime()
        
    def get_document(self):
        """Get the document."""
        return self.aq_inner
        
#    def manage_afterClone(self, obj):
#        """We were copied, make sure we're not public.
#        """
#        # if we don't have any public version we're fine
#        if not self.get_public_version():
#            return
#        # close any public version
#        self.close_version()


    #def index_html(self, REQUEST=None, RESPONSE=None):
    #    """Get rendered document.
    #    """
    #    if RESPONSE:
    #        RESPONSE.setHeader('Content-Type', 'text/xml')
    #    return self.doc.index_html(REQUEST, RESPONSE)

    def document_url(self):
        """Get document URL."""
        return self.absolute_url()

    def xml_url(self):
        """Get URL for xml data.
        """
        return self.absolute_url() + '/' + self.get_unapproved_version()
    
    def create_copy(self):
        """Create new version of public version.
        """
        if self.get_next_version() is not None:
            return
        
        # if there is no next version, get copy of public version
        published_version_id = self.get_public_version()
        # copy published version
        new_version_id = str(self._version_count)
        self._version_count = self._version_count + 1
        self.manage_clone(getattr(self, published_version_id),
                          new_version_id,
                          self.REQUEST)
        self.create_version(new_version_id, None, None)
        
    def editor(self):
        """Show document in editor mode.
        """
        # now show unapproved version in editor
        version_id = self.get_unapproved_version()
        if version_id is None:
            if self.get_next_version():
                return "Unapprove version first to edit."
            else:
                return "There is no unpublished version [make copy]"
        doc = getattr(self, version_id)
        wm = self.wm
        node = wm.get_widget_node(doc.documentElement)
        return node.render(node, self.REQUEST)

    def preview(self):
        """Preview document as HTML
        """
        version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_public_version()
            if version_id is None:
                return "There is no document to preview."
        doc = getattr(self, version_id)
        view_wm = self.view_wm
        node = view_wm.get_widget_node(doc.documentElement)
        return node.render(node, self.REQUEST)

    def view(self):
        """View document as HTML
        """
        version_id = self.get_public_version()
        if version_id is None:
            return "There is no public version."
        doc = getattr(self, version_id)
        view_wm = self.view_wm
        node = view_wm.get_widget_node(doc.documentElement)
        return node.render(node, self.REQUEST)

    def public(self):
        """Get version open to the public.
        """
        version_id = self.get_public_version()
        if version_id is None:
            return None # There is no public document
        doc = getattr(self, version_id)
        view_wm = self.view_wm
        node = view_wm.get_widget_node(doc.documentElement)
        return node.render(node, self.REQUEST)

    def is_published(self):
        """Return true if this is published.
        """
        return self.get_public_version() is not None
        
    security.declareProtected('Access contents information',
                              'get_metadata')
    def get_metadata(self, name):
        """Get meta data.
        """
        return self._metadata.get(name, None)
    
    security.declareProtected('Change Silva Documents',
                              'set_metadata')
    def set_metadata(self, name, value):
        """Set meta data.
        """
        if not self._metadata.has_key(name):
            return
        self._metadata[name] = value
        self._metadata = self._metadata
        
    def to_folder(self):
        """Convert this document to folder in same place.
        """
        # get id of document; this will be the id of the folder
        id = self.id
        # we will rename ourselves to a temporary id
        temp_id = 'silva_temp_%s' % id
        # get parent folder
        parent = self.get_folder()
        # rename doc so we can create folder with the same name
        parent.manage_renameObject(id, temp_id)
        # create Silva Folder to hold self
        parent.manage_addProduct['Silva'].manage_addFolder(id, self.title(), 0)
        # get folder
        folder = getattr(parent, id)
        # now add self to folder
        cb = parent.manage_cutObjects([temp_id])
        folder.manage_pasteObjects(cb_copy_data=cb)
        # rename doc from temp_id to 'doc'
        folder.manage_renameObject(temp_id, 'doc')
        return folder
    
    def action_paste(self, REQUEST):
        """Convert this to Folder and paste objects on clipboard.
        """
        # convert myself to a folder
        folder = self.to_folder()
        # paste stuff into the folder
        folder.action_paste(REQUEST)
    
    def get_modification_datetime(self):
        """Get modification date.
        """
        doc_id = self.get_next_version() or self.get_public_version()
        if doc_id is not None:
            return getattr(self, doc_id).bobobase_modification_time()
        else:
            return None

    def get_unpublished_status(self):
        """Get status of unpublished document.
        """
        if self.get_unapproved_version() is not None:
            return "not_approved"
        elif self.get_approved_version() is not None:
            return "approved"
        else:
            return "no_next"

    def get_published_status(self):
        if self.get_public_version() is not None:
            return "published"
        elif self.get_previous_versions():
            return "closed"
        else:
            return "no_published"
        
    def render_text_as_html(self, node):
        """Render textual content as HTML.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(escape(child.data, 1))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('<strong>')
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</strong>')
            elif child.nodeName == 'em':
                result.append('<em>')
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</em>')
            elif child.nodeName == 'link':
                result.append('<a href="%s">' %
                              escape(child.getAttribute('url'), 1))
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</a>')
            elif child.nodeName == 'ref':
                result.append('<a name="%s">' %
                              escape(child.getAttribute('name'), 1))
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</a>')
            else:
                raise "Unknown element: %s" % child.nodeName
        return ''.join(result)
        
    def render_text_as_editable(self, node):
        """Render textual content as editable text.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(child.data)
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('**')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('**')
            elif child.nodeName == 'em':
                result.append('++')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('++')
            elif child.nodeName == 'link':
                result.append('__')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('|')
                result.append(child.getAttribute('url'))
                result.append('__')
            elif child.nodeName == 'ref':
                result.append('[[')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('|')
                result.append(child.getAttribute('name'))
                result.append(']]')
            else:
                raise "Unknown element: %s" % child.nodeName

        return ''.join(result)
    
    _strongStructure = ForgivingParser.Structure(['**', '**'])
    _emStructure = ForgivingParser.Structure(['++', '++'])
    _linkStructure = ForgivingParser.Structure(['__', '|', '__'])
    _refStructure = ForgivingParser.Structure(['[[', '|', ']]'])
    
    _parser = ForgivingParser.ForgivingParser([
        _strongStructure,
        _emStructure,
        _linkStructure,
        _refStructure])
    
    def replace_text(self, node, text):
        """Replace text in a text containing node.
        """
        #text = escape(text, 1)
        
        # parse the data
        result = self._parser.parse(text)

        # get actual DOM node
        node = node._node
        doc = node.ownerDocument
        
        # remove all old subnodes of node
        # FIXME: hack to make copy of all childnodes
        children = [child for child in node.childNodes]
        children.reverse()  
        for child in children:
            node.removeChild(child)
            
        # now use tokens in result to add them to XML
        for structure, data in result:
            if structure is None:
                # create a text node, data is plain text
                newnode = doc.createTextNode(data)
                node.appendChild(newnode)
            elif structure is Document._strongStructure:
                newnode = doc.createElement('strong')
                newnode.appendChild(doc.createTextNode(data[0]))
                node.appendChild(newnode)
            elif structure is Document._emStructure:
                newnode = doc.createElement('em')
                newnode.appendChild(doc.createTextNode(data[0]))
                node.appendChild(newnode)
            elif structure is Document._linkStructure:
                link_text, link_url = data
                newnode = doc.createElement('link')
                newnode.appendChild(doc.createTextNode(link_text))
                newnode.setAttribute('url', link_url)
                node.appendChild(newnode) 
            elif structure is Document._refStructure:
                ref_text, ref_name = data
                newnode = doc.createElement('ref')
                newnode.appendChild(doc.createTextNode(ref_text))
                newnode.setAttribute('name', ref_name)
                node.appendChild(newnode) 
            else:
                raise "Unknown structure: %s" % structure

Globals.InitializeClass(Document)

manage_addDocumentForm = PageTemplateFile("www/documentAdd", globals(),
                                          __name__='manage_addDocumentForm')

def manage_addDocument(self, id, title, REQUEST=None):
    """Add a Document."""
    object = Document(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add empty ParsedXML object
    str = """<doc></doc>"""
    object.manage_addProduct['ParsedXML'].manage_addParsedXML('0', '', str)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''



