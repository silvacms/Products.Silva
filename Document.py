# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
import SilvaPermissions

# Silva
from VersionedContent import VersionedContent
import ForgivingParser
import Interfaces
# misc
from helpers import add_and_edit
from cgi import escape

class Document(VersionedContent):
    """Silva Document.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Document"

    __implements__ = Interfaces.VersionedContent
         
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
        
    def __repr__(self):
        return "<Silva Document instance at %s>" % self.id

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

    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'xml_url')
    def xml_url(self):
        """Get URL for xml data.
        """
        return self.absolute_url() + '/' + self.get_unapproved_version()

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
        if name == 'title':
            return self.get_title()
        return self._metadata.get(name, None)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_metadata')
    def set_metadata(self, name, value):
        """Set meta data.
        """
        if name == 'title':
            self.set_title(value)
            return
        if not self._metadata.has_key(name):
            return
        self._metadata[name] = value
        self._metadata = self._metadata

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Convert this document to folder in same place.
        """
        # get id of document; this will be the id of the folder
        id = self.id
        # we will rename ourselves to a temporary id
        temp_id = 'silva_temp_%s' % id
        # get parent folder
        parent = self.get_container()
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_text_as_html')
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'render_text_as_editable')
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'replace_text')
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



