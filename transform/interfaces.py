from Interface import Interface

class IRenderable(Interface):
    """I'm implemented by objects that can be rendered."""

    def getRendererId():
        """Returns a string that is the ID of the renderer which will
        be used to render the object."""

    def setRendererId():
        """Set the renderer to be used to display this object."""

    def getMetaType():
        """Return the meta type of this object."""

class IXMLSource(Interface):
    """I'm implemented by objects that use XML as their source content."""

    def getXML():
        """Return the XML content."""

class IRenderer(Interface):
    """I'm implemented by objects that can render other objects."""

    def render(obj):
        """Renders obj; returns the rendering as a string."""

    def getName():
        """Return the human-readable name of this renderer."""

class IRendererRegistry(Interface):
    """I'm implemented by something that tracks the existence of
    renderers, and the meta types to which they can be applied."""

    def getRenderersForMetaType(meta_type):
        """Return a list of objects, each representing a factory
        that can create an object to render the give meta_type."""

    def getRendererById(renderer_id, meta_type):
        """Return a renderer factory by its string ID."""
