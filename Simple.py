# Zope
from OFS import ObjectManager, SimpleItem
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
# XA
from ViewRegistry import ViewAttribute
from Versioning import Versioning
# misc
from helpers import add_and_edit

class Simple(ObjectManager.ObjectManager,
             SimpleItem.Item,
             Versioning):
    """Simple test
    """
    meta_type = "XA Simple"

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
    
    manage_editForm = PageTemplateFile('www/simpleEdit', globals(),
                                       __name__='manage_main')
    manage_previewForm = PageTemplateFile('www/simplePreview', globals(),
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
        self.title = title
        
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Get rendered document.
        """
        return self.get_public_version() or 'No version'

    def preview(self, REQUEST=None, RESPONSE=None):
        """Get preview of document.
        """
        return self.get_next_version() or 'No version'

    def document_url(self):
        """Get document URL."""
        return self.absolute_url()
    
Globals.InitializeClass(Simple)

manage_addSimpleForm = PageTemplateFile("www/simpleAdd", globals(),
                                        __name__='manage_addSimpleForm')

def manage_addSimple(self, id, title, REQUEST=None):
    """Add a Simple."""
    object = Simple(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # create a version
    object.create_version('first', None, None)
    add_and_edit(self, id, REQUEST)
    return ''



