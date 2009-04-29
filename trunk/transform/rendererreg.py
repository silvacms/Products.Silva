from zope.interface import implements

from Products.Silva.transform.interfaces import IRendererRegistry

class RendererRegistry(object):

    implements(IRendererRegistry)

    def __init__(self):
        self._renderers = {}

    def registerRenderer(self, meta_type, renderer_name, renderer_class):
        """Register a class as a renderer for a meta type under a name.
        """
        self._renderers.setdefault(meta_type, {})[renderer_name] = renderer_class

    def unregisterRenderer(self, meta_type, renderer_name):
        """Register a class as a renderer for a meta type under a name.
        """
        del self._renderers.setdefault(meta_type, {})[renderer_name]
        
    def getRenderersForMetaType(self, meta_type):
        """Return a dictionary of registered renderers for this meta type
        """
        return self._renderers.get(meta_type)
    
    def getMetaTypes(self):
        """Return a list of all meta types for which nay renderers are are 
        registered.
        """
        return self._renderers.keys()

_REGISTRY = RendererRegistry()

def getRendererRegistry():
    return _REGISTRY
