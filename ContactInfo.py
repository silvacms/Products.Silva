from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
from Asset import Asset
import Interfaces
import SilvaPermissions
# misc
from helpers import add_and_edit

class ContactInfo(Asset):
    """Contact Info
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Contact Info"

    __implements__ = Interfaces.Asset

    def __init__(self, id, title):
        self.id = id
        self._title = title
        self._data = {}

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_data')
    def set_data(self, dict):
        """Set the data dictionary.
        """
        # FIXME: should really do check whether all keys are of right
        # format, but formulator does that so well already..
        self._data = dict

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_data')
    def get_data(self):
        """Get the data dictionary.
        """
        return self._data
    
InitializeClass(ContactInfo)

manage_addContactInfoForm = PageTemplateFile("www/contactInfoAdd", globals(),
                                             __name__='manage_addContactInfoForm')

def manage_addContactInfo(self, id, title, REQUEST=None):
    """Add a ContactInfo."""
    object = ContactInfo(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
