# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Silva
from Folder import Folder
import Interfaces
import SilvaPermissions
#misc
from helpers import add_and_edit

class Publication(Folder):
    """Publication.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Publication"

    __implements__ = Interfaces.Container


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_publication')
    def get_publication(self):
        """Get publication. Can be used with acquisition get the
        'nearest' Silva publication.
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'is_transparent')
    def is_transparent(self):
        return 0

InitializeClass(Publication)

manage_addPublicationForm = PageTemplateFile("www/publicationAdd", globals(),
                                             __name__='manage_addPublicationForm')

def manage_addPublication(self, id, title, REQUEST=None):
    """Add a Silva publication."""
    if not self.is_id_valid(id):
        return
    object = Publication(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
