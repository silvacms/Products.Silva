from Products.Silva.transform.interfaces import IRendererRegistry

# XXX: no real renderers yet
_REGISTRY = {'Silva Document' : None}

class RendererRegistry(object):

    __implements__ = IRendererRegistry

    def __init__(self):
        self._registry = _REGISTRY

    def getRendererById(self, renderer_id, meta_type):
        meta_type_renderers = self._registry.get(meta_type, None)
        for r in meta_type_renderers:
            if r.getId() == renderer_id:
                return r

    def getRenderersForMetaType(self, meta_type):
        return self._registry.get(meta_type, [])
