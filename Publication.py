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
        orig_id = self.id
        convert_id = 'convert__%s' % orig_id
        container.manage_addProduct['Silva'].manage_addFolder(
            convert_id, self.get_title(), create_default=0)
        publication = getattr(container, convert_id)
        # copy all contents into new folder
        cb = self.manage_copyObjects(self.objectIds())
        publication.manage_pasteObjects(cb)
        # copy over all properties
        for key, value in self.propertyItems():
            publication.manage_addProperty(
                key, value, self.getPropertyKey(key))
        # copy over authorization info
        for userid in self.sec_get_userids():
            roles = self.sec_get_roles_for_userid(userid)
            for role in roles:
                publication.sec_assign(userid, role)
        # now remove this object from the container
        container.manage_delObjects([self.id])
        # and rename the copy
        container.manage_renameObject(convert_id, orig_id)
        
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
