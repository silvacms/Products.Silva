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

    __implements__ = Interfaces.Publication

    # MANIPULATORS
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_folder')
    def to_folder(self):
        """Publication becomes a folder instead.
        """
        # first create new folder
        container = self.get_container()
        container.manage_addProduct['Silva'].manage_addFolder(
            'convert__%s' % self.id, self.get_title(), create_default=0)
        # copy all contents into new folder
        cp = self.manage_copyObjects(self.objectIds())
        # copy over all properties
        for key, value in self.propertyItems():
            self.manage_addProperty(key, value, self.getPropertyKey(key))
        # copy over authorization info
        for userid in self.sec_get_userids():
            pass
        
    # ACCESSORS
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_publication')
    def get_publication(self):
        """Get publication. Can be used with acquisition to get
        'nearest' Silva publication.
        """
        return self.aq_inner
    
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'is_transparent')
    def is_transparent(self):
        return 0

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, f):
        """Render object to XML.
        """
        f.write('<silva_publication id="%s">' % self.id)
        self._to_xml_helper(f)
        f.write('</silva_publication>')


InitializeClass(Publication)

manage_addPublicationForm = PageTemplateFile("www/publicationAdd", globals(),
                                             __name__='manage_addPublicationForm')

def manage_addPublication(self, id, title, create_default=1, REQUEST=None):
    """Add a Silva publication."""
    if not self.is_id_valid(id):
        return
    object = Publication(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add doc
    if create_default:
        object.manage_addProduct['Silva'].manage_addDocument('index', '')
    add_and_edit(self, id, REQUEST)
    return ''
