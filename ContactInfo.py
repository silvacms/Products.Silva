# Version: $Revision: 1.8 $
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
        ContactInfo.inheritedAttribute('__init__')(self, id, 'No title for ContactInfo')
        self._data = { 'contact_name': title }

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_data')
    def set_data(self, dict):
        """Set the data dictionary.
        """
        # FIXME: should really do check whether all keys are of right
        # format, but formulator does that so well already..
        self._data = dict

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        # should set title through setting the data, as we don't
        # want any title rename field to be able to change the
        # name of a contact info that can be used in quite a few places
        pass

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_title')
    def get_title(self):
        return self._data['contact_name']
    
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
    if not self.is_id_valid(id):
        return
    object = ContactInfo(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
