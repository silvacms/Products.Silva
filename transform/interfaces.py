from Interface import Interface

class IRenderable(Interface):
    """I'm implemented by objects that can be rendered."""

    def getRendererName():
        """Returns a string that is the name of the renderer
        which will be used to render the object."""
        pass

    def getMetaType():
        """Return the meta type of this object."""
        pass

class IXMLSource(Interface):
    """I'm implemented by objects that use XML as their source content."""

    def getXML():
        """Return the XML content."""

class IRenderer(Interface):
    """I'm implemented by objects that can render other objects."""

    def render(obj):
        """Renders obj; returns the rendering as a string."""

    def setName(name):
        """Set a human-readable name for this renderer, e.g.
        'Lower-case all text.'"""

    def getName():
        """Return the human-readable name of this renderer."""

    def getId():
        """Get the ID of the object."""

    def setId(renderer_id):
        """Set the ID of the object."""

    def supportsMetaType(meta_type):
        """Is this meta type supported by this renderer?"""

    def getSupportedMetaTypes():
        """Returns a list of strings, which are the names of all
        meta types that this renderer supports."""

    def setSupportedMetaTypes(meta_types):
        """Takes a list of meta types that this renderer supports."""

class IRendererRegistry(Interface):
    """I'm implemented by something that tracks the existence of
    renderers, and the meta types to which they can be applied."""

    def getRenderersForMetaType(meta_type):
        """Return a list of objects, each representing a factory
        that can create an object to render the give meta_type."""

    def getRendererById(renderer_id, meta_type):
        """Return a renderer factory by its string ID."""
