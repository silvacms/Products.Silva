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
                
    security.declareProtected('View management screens',
                              'merge_tree')
    def merge_tree(self, main_tree, install_tree):
        """Merge install_tree into main_tree
        """
        for object in install_tree.objectValues():
            if object.meta_type == 'Folder':
                if not hasattr(main_tree.aq_base, object.id):
                    main_tree.manage_addFolder(object.id, '')    
                self.merge_tree(getattr(main_tree, object.id), object)
            else:
                if not hasattr(main_tree.aq_base, object.id):
                    cb = install_tree.manage_copyObjects([object.id])
                    main_tree.manage_pasteObjects(cb_copy_data=cb)
                    
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
        f.write('<silva_root id="%s">' % self.id)
        self._to_xml_helper(f)
        f.write('</silva_root>')

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'get_silva_addables_allowed_in_publication')
    def get_silva_addables_allowed_in_publication(self):
        # allow everything in silva by default, unless things are restricted
        # explicitly
        addables = self._addables_allowed_in_publication
        if addables is None:
            return self.get_silva_addables_all()
        else:
            return addables
        
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
