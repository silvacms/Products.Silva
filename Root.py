# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Silva
from Publication import Publication
import Interfaces
import SilvaPermissions
#misc
from helpers import add_and_edit

class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Root"

    __implements__ = Interfaces.Publication
    
    # MANIPULATORS

    def manage_afterAdd(self, item, container):
        # since we're root, we don't want to notify our container
        pass
        
    def manage_beforeDelete(self, item, container):
        # since we're root, we don't want to notify our container
        pass
    
    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_root')
    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, f):
        """Render object to XML.
        """
        f.write('<silva_root>')
        self._to_xml_helper(f)
        f.write('</silva_root>')


    #security.declareProtected(SilvaPermissions.ChangeSilvaContent,
    #                          'get_view')
    #def get_view(self, view_type, obj):
    #    """Get a view for an object from the view registry.
    #    """
    #    return self.service_view_registry.wrap(view_type, obj)
    
InitializeClass(Root)

manage_addRootForm = PageTemplateFile("www/rootAdd", globals(),
                                      __name__='manage_addRootForm')

def manage_addRoot(self, id, title, REQUEST=None):
    """Add a Silva root."""
    # no id check possible or necessary, as this only happens rarely and the
    # Zope id check is fine
    object = Root(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add all services
    #silva = object.manage_addProduct['Silva']
    #silva.manage_addViewRegistry('service_view_registry')

    add_and_edit(self, id, REQUEST)
    return ''
