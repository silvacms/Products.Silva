# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Zope
from AccessControl import ClassSecurityInfo

# Silva
from Products.Silva.transform.RendererRegistry import RendererRegistry
from Products.Silva.transform.renderers.RenderImagesOnRight import RenderImagesOnRight
from Products.Silva.transform.renderers.BasicHTMLRenderer import BasicHTMLRenderer
from Products.Silva.transform.renderers.BasicRenderer import BasicRenderer
import SilvaPermissions
from helpers import add_and_edit

class RendererRegistryService(SimpleItem.SimpleItem):
    """An addable Zope product which registers information
    about content renderers."""

    meta_type = "Silva Renderer Registry Service"
    manage_options = SimpleItem.SimpleItem.manage_options + (
        {'label' : 'Default Renderers', 'action' : 'manage_default_renderers'},)

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.default_renderer = {'Silva Document Version' : "Basic HTML"}

    def getRendererRegistry(self):
        # XXX: nasty hack for now, because I can't assign the registry to a simple
        # attribute of self, as it won't play nicely with the persistence machinery
        #
        # we might want to clean this up after the beta
        renderers = [BasicHTMLRenderer().__of__(self)]
        try:
            import libxslt
        except ImportError:
            pass
        else:
            renderers.append(RenderImagesOnRight().__of__(self))
            renderers.append(BasicRenderer().__of__(self))

        return {'Silva Document Version' : renderers}

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_default_renderers')
    manage_default_renderers = PageTemplateFile(
        "www/serviceRendererRegistryDefaultRenderersEdit", globals())

    security.declareProtected(
        SilvaPermissions.ViewManagementScreens, 'manage_editDefaultRenderers')
    def manage_editDefaultRenderers(self, REQUEST=None):
        """Save the changes to the default renderers."""
        if not hasattr(self, 'default_renderer'):
                self.default_renderer = {'Silva Document Version' : "Basic HTML"}

        for meta_type in self.getRegisteredContentTypes():
            field_name = meta_type.replace(" ", "_")
            self.default_renderer[meta_type] = REQUEST.get(field_name, None)
            self._p_changed = 1

        return self.manage_default_renderers()

    security.declareProtected("View", "getRenderersForMetaType")
    def getRenderersForMetaType(self, meta_type):
        # FIXME: this is really pretty terrible, but there's a demo in a week
        # and customers don't pay for coding elegance. a more sound way
        # of relating this, Zope-specific code to the normal Python renderer
        # registry code should definintely be revisted after the Aug 16 demo.
        return self.getRendererRegistry()[meta_type]

    def getRendererByName(self, name, meta_type):
        meta_type_renderers = self.getRenderersForMetaType(meta_type)
        for r in meta_type_renderers:
            if r.getName() == name:
                return r

        return None

    def getRegisteredContentTypes(self):
        return self.getRendererRegistry().keys()

    def getDefaultRendererNameForMetaType(self, meta_type):
        if not hasattr(self, 'default_renderer'):
            self.default_renderer = {'Silva Document Version' : "Basic HTML"}
            self._p_changed = 1
        return self.default_renderer.get(meta_type, None)

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

