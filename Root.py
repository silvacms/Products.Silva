# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
# Silva
from Folder import Folder
# misc
from helpers import add_and_edit

class Root(Folder):
    """Root of Silva site.
    """
    meta_type = "Silva Root"

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self._title = title

    def __repr__(self):
        return "<Silva Root instance at %s>" % self.id

    def get_root(self):
        """Get root of site.
        """
        return self.aq_inner

    #def __bobo_traverse__(self, request, key):
    #    """Put in skin layer just below root.
    #    """
    #    # FIXME: only handle Silva Folder skin now..
    #    r = self.service_view_registry
    #    skin = getattr(r, r.view_types['edit']['Silva Folder'])
    #    return getattr(self.__of__(skin), key)
    
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
