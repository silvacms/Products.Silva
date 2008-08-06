from zope.interface import Interface, Attribute

class IRenderable(Interface):
    """I'm implemented by objects that can be rendered."""

    def preview():
        """Display the preview of this object using the selected renderer.
        
        Returns the rendered content or None if no renderer can be
        found.
        """
        
    def view():
        """Display the view of this object using the selected renderer.
        
        Returns the rendered content or None if no renderer can be
        found.
        """
        
class IXMLSource(Interface):
    """I'm implemented by objects that use XML as their source content."""

    def getXML():
        """Return the XML content."""

class IRenderer(Interface):
    """I'm implemented by objects that can render other objects."""

    meta_type = Attribute(u"Meta type rendered by this renderer")
    title = Attribute(u"Name for the renderer")

    def render(obj):
        """Renders obj; returns the rendering as a string."""

class IRendererRegistry(Interface):
    """I'm implemented by something that tracks the existence of
    renderers, and the meta types to which they can be applied."""

    def registerRenderer(meta_type, renderer_name, renderer_class):
        """Register a class as a renderer for a meta type under a name.
        """
        
    def getRenderersForMetaType(self, meta_type):
        """Return a dictionary of registered renderers for this meta type
        """

    def getMetaTypes(self):
        """Return a list of all meta types for which nay renderers are are 
        registered.
        """
