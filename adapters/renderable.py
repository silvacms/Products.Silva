import Globals
from Products.Silva.adapters import adapter
from Products.Silva.transform.interfaces import IRenderable
from Products.Silva.transform.Exceptions import InvalidRendererError

class RenderableAdapter(adapter.Adapter):

    __implements__ = IRenderable

    def setRendererId(self, renderer_id):
        metadata_system = self.context.service_metadata
        binding = metadata_system.getMetadata(self.context.get_editable())
        binding.setValues(
            'silva-extra', {'renderer_id' : renderer_id}, reindex = 1)

    def getRendererId(self):
        metadata_system = self.context.service_metadata
        binding = metadata_system.getMetadata(self.context.get_editable())
        return binding['silva-extra']['renderer_id']

    def getMetaType(self):
        pass

Globals.InitializeClass(RenderableAdapter)

def getRenderableAdapter(context):
    return RenderableAdapter(context).__of__(context)
    