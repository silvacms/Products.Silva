# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
import OFS
# Silva
from Asset import Asset
import Interfaces
import SilvaPermissions
# misc
from helpers import add_and_edit

class Image(Asset):
    """Image object.
    """    
    security = ClassSecurityInfo()

    meta_type = "Silva Image"

    __implements__ = Interfaces.Asset
    
    def __init__(self, id, title):
        Image.inheritedAttribute('__init__')(self, id, title)
        self.image = None # should create default image

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'image')
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_image')
    def set_image(self, file):
        """Set the image object.
        """
        self.image = OFS.Image.Image('image', 'No image title', file)
    
InitializeClass(Image)
    
manage_addImageForm = PageTemplateFile("www/imageAdd", globals(),
                                       __name__='manage_addImageForm')

def manage_addImage(self, id, title, REQUEST=None):
    """Add a Image."""
    if not self.is_id_valid(id):
        return
    object = Image(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
