# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Zope
from AccessControl import ClassSecurityInfo

# Silva
from Products.Silva.transform.rendererreg import getRendererRegistry
import SilvaPermissions
from helpers import add_and_edit

class RendererRegistryService(SimpleItem.SimpleItem):
    """An addable Zope product which registers information
    about content renderers."""

    security = ClassSecurityInfo()
    
    meta_type = "Silva Renderer Registry Service"
    manage_options = (
        {'label': 'Renderers', 'action': 'manage_renderers'},
        ) + SimpleItem.SimpleItem.manage_options

    security.declareProtected(
        'View management screens', 'manage_renderers')
    manage_renderers = PageTemplateFile(
        'www/serviceRendererRegistryDefaultRenderersEdit', globals(), 
        __name__='manage_renderers')
        
    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._default_renderers = {}

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_default_renderers')
    manage_default_renderers = PageTemplateFile(
        "www/serviceRendererRegistryDefaultRenderersEdit", globals())

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'getFormRenderersList')
    def getFormRenderersList(self, meta_type):
        result = ['(Default)']
        for renderer_name in self.getRendererNamesForMetaType(meta_type):
            result.append(renderer_name)
        return result
    
    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editDefaultRenderers')
    def manage_editDefaultRenderers(self, REQUEST=None):
        """Save the changes to the default renderers."""

        for meta_type in self.getRegisteredMetaTypes():
            field_name = meta_type.replace(" ", "_")
            self.registerDefaultRenderer(meta_type, REQUEST.get(field_name, None))

        return self.manage_default_renderers()

    def registerDefaultRenderer(self, meta_type, renderer_name):
        if renderer_name == '(None)':
            renderer_name = None
        self._default_renderers[meta_type] = renderer_name
        self._p_changed = 1
       
    security.declarePrivate('getRenderer')
    def getRenderer(self, meta_type, renderer_name):
        """Get renderer registered for meta_type/renderer_name combination.

        If renderer_name is None, the default renderer name is looked up
        first.
        
        If no renderers can be found for meta_type, or specifically named
        renderer cannot be found for this meta_type, None is returned.
        """
        if renderer_name is None:
            renderer_name = self._default_renderers.get(meta_type)
        renderer_dict = self._getRendererDict(meta_type)
        if renderer_dict is None:
            return None
        return renderer_dict.get(renderer_name)
              
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 
        "getRendererNamesForMetaType")
    def getRendererNamesForMetaType(self, meta_type):
        """Get a list of all renderer names registered for meta_type.
        """
        # XXX sorting alphabetically, might want to order this explicitly
        renderer_names = self._getRendererDict(meta_type, {}).keys()
        renderer_names.sort()
        return renderer_names
   
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 
        "getRendererNamesForMetaType")
    def getRegisteredMetaTypes(self):
        """Get a list of all meta types that have renderers registered.
        """
        meta_types = getRendererRegistry().getMetaTypes()
        meta_types.sort()
        return meta_types

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        "getDefaultRendererNameForMetaType")
    def getDefaultRendererNameForMetaType(self, meta_type):
        """Get the default renderer registered for the meta type.
        
        If no default renderer is registered return None.
        """
        return self._default_renderers.get(meta_type)

    def doesRendererExistForMetaType(self, meta_type, renderer_name):
        return self._getRendererDict(meta_type, {}).has_key(renderer_name)
    
    # PRIVATE
    def _getRendererDict(self, meta_type, default=None):
        result = getRendererRegistry().getRenderersForMetaType(meta_type)
        if result is None:
            return default
        return result
    
InitializeClass(RendererRegistryService)

manage_addRendererRegistryServiceForm = PageTemplateFile(
    "www/rendererRegistryServiceAdd", globals())

def manage_addRendererRegistryService(self, id, title="", REQUEST=None):
    """Add renderer registry service."""
    obj = RendererRegistryService(id, title)
    self._setObject(id, obj)
    ob = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''

