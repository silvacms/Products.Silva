from Products.Silva.transform.interfaces import IRendererRegistry

try:
    import libxslt
    import libxml2
except ImportError:
    _REGISTRY = {}
else:
    from Products.Silva.transform.renderer.imagesonrightrenderer import ImagesOnRightRenderer
    from Products.Silva.transform.renderer.basicxsltrenderer import BasicXSLTRenderer
    _REGISTRY = {'Silva Document Version' : [ImagesOnRightRenderer(), BasicXSLTRenderer()]}

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
