# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements

from Products.Silva.transform.interfaces import IRendererRegistry

class RendererRegistry(object):

    implements(IRendererRegistry)

    def __init__(self):
        self.__renderers = {}

    def registerRenderer(self, meta_type, name, renderer):
        """Register a class as a renderer for a meta type under a name.
        """
        self.__renderers.setdefault(meta_type, {})[name] = renderer

    def unregisterRenderer(self, meta_type, name):
        """Register a class as a renderer for a meta type under a name.
        """
        del self.__renderers.setdefault(meta_type, {})[name]

    def getRenderersForMetaType(self, meta_type):
        """Return a dictionary of registered renderers for this meta type
        """
        return self.__renderers.get(meta_type)

    def getMetaTypes(self):
        """Return a list of all meta types for which nay renderers are are
        registered.
        """
        return self.__renderers.keys()

_REGISTRY = RendererRegistry()

def getRendererRegistry():
    return _REGISTRY
