# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

# Silva
from Products.Silva.transform.rendererreg import getRendererRegistry
import SilvaPermissions
from helpers import add_and_edit
from BaseService import SilvaService

from silva.core import conf as silvaconf

OLD_STYLE_RENDERER = 'Do not use new-style renderer'

class RendererRegistryService(SilvaService):
    """An addable Zope product which registers information
    about content renderers."""

    security = ClassSecurityInfo()
    
    meta_type = "Silva Renderer Registry Service"
    manage_options = (
        {'label': 'Renderers', 'action': 'manage_renderers'},
        ) + SilvaService.manage_options

    security.declareProtected(
        'View management screens', 'manage_renderers')
    manage_renderers = PageTemplateFile(
        'www/serviceRendererRegistryDefaultRenderersEdit', globals(), 
        __name__='manage_renderers')
        
    security = ClassSecurityInfo()

    silvaconf.icon('www/renderer_service.png')
    silvaconf.factory('manage_addRendererRegistryServiceForm')
    silvaconf.factory('manage_addRendererRegistryService')

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self._default_renderers = {}

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_default_renderers')
    manage_default_renderers = PageTemplateFile(
        "www/serviceRendererRegistryDefaultRenderersEdit", globals())

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editDefaultRenderers')
    def manage_editDefaultRenderers(self, REQUEST=None):
        """Save the changes to the default renderers."""

        for meta_type in self.getRegisteredMetaTypes():
            field_name = meta_type.replace(" ", "_")
            self.registerDefaultRenderer(
                meta_type,
                REQUEST.get(field_name, None))

        return self.manage_default_renderers()

    security.declarePublic('getFormRenderersList')
    def getFormRenderersList(self, meta_type):
        return ['(Default)'] + self.getRendererNamesForMetaType(meta_type)
       
    security.declarePublic('doesRendererExistForMetaType')
    def doesRendererExistForMetaType(self, meta_type, renderer_name):
        """Returns true if a renderer is registered for a meta type.

        Rendererer is always known if it's old style.
        """
        d = self._getRendererDict(meta_type)
        if d is None:
            return False
        if renderer_name == OLD_STYLE_RENDERER:
            return True
        return d.has_key(renderer_name)
    
    security.declarePrivate('getRenderer')
    def getRenderer(self, meta_type, renderer_name):
        """Get renderer registered for meta_type/renderer_name combination.

        If renderer_name is None, the default renderer name is looked up
        first.

        If renderer name is the old style renderer, None is returned,
        triggering a fall-back onto the old style renderer.
        
        If no renderers can be found for meta_type, or specifically named
        renderer cannot be found for this meta_type, None is returned,
        triggering the fall-back as well.
        """
        if renderer_name == OLD_STYLE_RENDERER:
            return None
        if renderer_name is None:
            renderer_name = self._default_renderers.get(meta_type)
        renderer_dict = self._getRendererDict(meta_type)
        if renderer_dict is None:
            return None
        return renderer_dict.get(renderer_name)

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'registerDefaultRenderer')
    def registerDefaultRenderer(self, meta_type, renderer_name):
        if renderer_name == '(Default)':
            renderer_name = None
        self._default_renderers[meta_type] = renderer_name
        self._p_changed = 1
 
    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
        "getRendererNamesForMetaType")
    def getRendererNamesForMetaType(self, meta_type):
        """Get a list of all renderer names registered for meta_type.

        Returns the empty list if no renderers are registered at all.
        Always adds the old style renderer otherwise.
        """
        # XXX sorting alphabetically, might want to order this explicitly
        renderer_names = self._getRendererDict(meta_type, {}).keys()
        if not renderer_names:
            return []
        renderer_names.sort()
        renderer_names = [OLD_STYLE_RENDERER] + renderer_names
        return renderer_names
   
    security.declareProtected(SilvaPermissions.ViewManagementScreens, 
        "getRendererNamesForMetaType")
    def getRegisteredMetaTypes(self):
        """Get a list of all meta types that have renderers registered.
        """
        meta_types = getRendererRegistry().getMetaTypes()
        meta_types.sort()
        return meta_types

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
         "getDefaultRendererNameForMetaType")
    def getDefaultRendererNameForMetaType(self, meta_type):
        """Get the default renderer registered for the meta type.
        
        If no default renderer is registered return None.
        """
        return self._default_renderers.get(meta_type)
    
    # PRIVATE
    def _getRendererDict(self, meta_type, default=None):
        result = getRendererRegistry().getRenderersForMetaType(meta_type)
        if result is None:
            return default
        return result
    
InitializeClass(RendererRegistryService)

manage_addRendererRegistryServiceForm = PageTemplateFile(
    "www/rendererRegistryServiceAdd", globals(),
    __name__='manage_addRendererRegistryServiceForm')

def manage_addRendererRegistryService(self, id, title="", REQUEST=None):
    """Add renderer registry service."""
    obj = RendererRegistryService(id, title)
    self._setObject(id, obj)
    ob = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''

