# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface


class IXMLSource(Interface):
    """I'm implemented by objects that use XML as their source content."""

    def getXML():
        """Return the XML content."""


class IRenderer(Interface):
    """I'm implemented by objects that can render other objects."""


    def transform(content, request):
        """Render content by get out the XML out of it. Return a string
        """

    def transform_xml(xml):
        """Render XML.
        """


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
