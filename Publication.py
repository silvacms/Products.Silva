# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
# Silva
from Folder import Folder
import Interfaces
#misc
from helpers import add_and_edit

class Publication(Folder):
    """Publication.
    """
    meta_type = "Silva Publication"

    __implements__ = Interfaces.Container
    
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        Publication.inheritedAttribute('__init__')(self, id, title)

    def __repr__(self):
        return "<Silva Publication instance at %s>" % self.id

    def get_publication(self):
        """Get publication. Can be used with acquisition get the
        'nearest' Silva publication.
        """
        return self.aq_inner
    
Globals.InitializeClass(Publication)

manage_addPublicationForm = PageTemplateFile("www/publicationAdd", globals(),
                                             __name__='manage_addPublicationForm')

def manage_addPublication(self, id, title, REQUEST=None):
    """Add a Silva publication."""
    object = Publication(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
