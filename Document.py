# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from Globals import InitializeClass
import SilvaPermissions

# Silva
from VersionedContent import VersionedContent
import Interfaces
from EditorSupport import EditorSupport

# misc
from helpers import add_and_edit, translateCdata

class Document(VersionedContent, EditorSupport):
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

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, f):
        """Render object to XML.
        """
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
#        parent.manage_addProduct['Silva'].manage_addFolder(id, self.title(), 0)
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



