from Products.Silva.transform.interfaces import IRendererRegistry
from Products.Silva.transform.renderers.RenderImagesOnRight import RenderImagesOnRight
from Products.Silva.transform.renderers.BasicRenderer import BasicRenderer

_REGISTRY = {'Silva Document Version' : [RenderImagesOnRight(), BasicRenderer()]}

class RendererRegistry(object):

    __implements__ = IRendererRegistry

    def __init__(self):
        self._registry = _REGISTRY

    def getRendererByName(self, name, meta_type):
        meta_type_renderers = self._registry.get(meta_type, None)
        for r in meta_type_renderers:
            if r.getName() == name:
                return r

    def getRenderersForMetaType(self, meta_type):
        return self._registry.get(meta_type, [])
