import Globals
from Products.Silva.adapters import adapter
from Products.Silva.transform.interfaces import IRenderable

class RenderableAdapter(adapter.Adapter):

    __implements__ = IRenderable

    def preview(self):
        """Display the preview of this object using the selected renderer.
        
        Returns the rendered content or None if no renderer can be
        found.
        """
        content = self.context.get_previewable()
        return self._view_helper(content)
    
    def view(self):
        """Display the view of this object using the selected renderer.
        
        Returns the rendered content or None if no renderer can be
        found.
        """
        content = self.context.get_viewable()
        return self._view_helper(content)
        
    def _view_helper(self, content):
        renderer_name = content.get_renderer_name()
        renderer = self.context.service_renderer_registry.getRenderer(
            content.get_silva_object().meta_type, renderer_name)
        if renderer is None:
            return None
        return renderer.render(content)
            
Globals.InitializeClass(RenderableAdapter)

def getRenderableAdapter(context):
    return RenderableAdapter(context).__of__(context)
    