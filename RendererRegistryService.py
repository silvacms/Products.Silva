# Zope
from OFS import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Zope
from AccessControl import ClassSecurityInfo

# Silva
from Products.Silva.transform.RendererRegistry import RendererRegistry
from Products.Silva.transform.renderers.RenderImagesOnRight import RenderImagesOnRight
from helpers import add_and_edit

class RendererRegistryService(SimpleItem.SimpleItem):
    """An addable Zope product which registers information
    about content renderers."""

    meta_type = "Silva Renderer Registry Service"

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        self.id = id
        self.title = title

    security.declareProtected("View", "getRenderersForMetaType")
    def getRenderersForMetaType(self, meta_type):
        # FIXME: this is really pretty terrible, but there's a demo in a week
        # and customers don't pay for coding elegance. a more sound way
        # of relating this, Zope-specific code to the normal Python renderer
        # registry code should definintely be revisted after the Aug 16 demo.
        REGISTRY = {'Silva Document Version' : [RenderImagesOnRight().__of__(self)]}
        return REGISTRY[meta_type]

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

