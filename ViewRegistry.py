# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.16 $
# Zope
import Acquisition
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from OFS import Folder, SimpleItem, ObjectManager, PropertyManager, FindSupport
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Globals
import SilvaPermissions
# misc
from helpers import add_and_edit

class ViewRegistry(Folder.Folder):
    """Silva View Registry.
    """
    meta_type = "Silva View Registry"

    security = ClassSecurityInfo()

    manage_options = (
      ( {'label':'Contents', 'action':'manage_main'},
        {'label':'Associations', 'action':'manage_associationsForm'} ) +\
        PropertyManager.PropertyManager.manage_options +\
      ( {'label':'Security', 'action':'manage_access'},
        {'label':'Undo', 'action':'manage_UndoForm'} ) +\
        FindSupport.FindSupport.manage_options 
      )

    manage_associationsForm = PageTemplateFile(
        'www/viewRegistryAssociations',
        globals(),  __name__='manage_assocationsForm')
    
    def __init__(self, id):
        self.id = id
        self.view_types = {}

    # MANIPULATORS
    
    security.declareProtected(SilvaPermissions.ChangeSilvaViewRegistry,
                              'register')
    def register(self, view_type, meta_type, view_path):
        """Register a view path with the registry. Can also be used
        to change what view path is registered.
        """
        self.view_types.setdefault(view_type, {})[meta_type] = view_path
        self.view_types = self.view_types

    security.declareProtected(SilvaPermissions.ChangeSilvaViewRegistry,
                              'unregister')
    def unregister(self, view_type, meta_type):
        """Unregister view_type, meta_type
        """
        del self.view_types[view_type][meta_type]
        self.view_types = self.view_types

    security.declareProtected(SilvaPermissions.ChangeSilvaViewRegistry,
                              'clear')
    def clear(self):
        """Clear all view_types associations.
        """
        self.view_types = {}
    
    # ACCESSORS
    
    def get_view_types(self):
        """Get all view types, sorted.
        """
        result = self.view_types.keys()
        result.sort()
        return result

    def get_meta_types(self, view_type):
        """Get meta_types registered for view_type, sorted.
        """
        meta_types = self.view_types.get(view_type, {})
        result = meta_types.keys()
        result.sort()
        return result

    def has_view(self, view_type, meta_type):
        """Return true if system has a view of this type.
        """
        try:
            self.view_types[view_type][meta_type]
            return 1
        except KeyError:
            return 0
        
    def get_view_path(self, view_type, meta_type):
        """Get view path used for view_type/meta_type combination.
        """
        return self.view_types[view_type][meta_type]

    def get_view(self, view_type, meta_type):
        """Get view for meta_type.
        """
        found = self
        for view_id in self.view_types[view_type][meta_type]:
            found = getattr(found, view_id, None)
        return found

    def render_preview(self, view_type, obj):
        """Render preview of object using view_registry. This calls
        the render_preview() method defined on the view in the registry.
        """
        self.REQUEST['model'] = obj
        return self.get_view(view_type,
                              obj.meta_type).render_preview()
    
    def render_view(self, view_type, obj):
        """Render view of object using view_registry. This calls
        the render_preview() method defined on the view in the registry.
        """
        self.REQUEST['model'] = obj
        return self.get_view(view_type,
                              obj.meta_type).render_view()

    def get_method_on_view(self, view_type, obj, name):
        """Get a method on the view for the object.
        """
        return getattr(self.get_view(view_type, obj.meta_type), name)
    
    #def wrap(self, view_type, obj):
    #    """Wrap object in view (wrapping skin)
    #    """
    #    return getattr(self,
    #                   self.view_types[view_type][obj.meta_type]).__of__(obj)
    
        #return obj.__of__(getattr(
        #    self, self.view_types[view_type][obj.meta_type]))
    
Globals.InitializeClass(ViewRegistry)

manage_addViewRegistryForm = PageTemplateFile(
    "www/viewRegistryAdd", globals(),
    __name__='manage_addViewRegistryForm')

def manage_addViewRegistry(self, id, REQUEST=None):
    """Add a ViewRegistry."""
    object = ViewRegistry(id)
    self._setObject(id, object)

    add_and_edit(self, id, REQUEST)
    return ''

class ViewAttribute(Acquisition.Implicit):
    def __init__(self, view_type, default_method):
        self._view_type = view_type
        self._default_method = default_method

    def index_html(self):
        """
        """
        return self[self._default_method]()
    
    def __getitem__(self, name):
        """
        """
        self.REQUEST['model'] = model = self.aq_parent
        return self.service_view_registry.get_method_on_view(
            self._view_type, model, name)
 
