# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
# Silva
from Folder import Folder
import Interfaces
#misc
from helpers import add_and_edit

class Root(Folder):
    """Root of Silva site.
    """
    meta_type = "Silva Root"

    __implements__ = Interfaces.Container
    
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        Root.inheritedAttribute('__init__')(self, id, title)

    # MANIPULATORS

    def manage_afterAdd(self, item, container):
        #self.inheritedAttribute('manage_afterAdd')(self, item, container)
        pass
        
    def manage_beforeDelete(self, item, container):
        #self.inheritedAttribute('manage_beforeDelete')(self, item, container)
        pass
    
    # ACCESSORS

    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner
    
    def get_view(self, view_type, obj):
        """Get a view for an object from the view registry.
        """
        return self.service_view_registry.wrap(view_type, obj)
    
Globals.InitializeClass(Root)

manage_addRootForm = PageTemplateFile("www/rootAdd", globals(),
                                      __name__='manage_addRootForm')

def manage_addRoot(self, id, title, REQUEST=None):
    """Add a Silva root."""
    object = Root(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    # add all services
    silva = object.manage_addProduct['Silva']
    silva.manage_addViewRegistry('service_view_registry')

    add_and_edit(self, id, REQUEST)
    return ''
