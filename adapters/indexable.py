# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core import interfaces

class IndexableAdapter(grok.Adapter):

    grok.implements(interfaces.IIndexable)
    grok.context(interfaces.ISilvaObject)

    def __init__(self, context):
        self.context = context

    def getTitle(self):
        return self.context.get_title()

    def getPath(self):
        return self.context.getPhysicalPath()

    def getIndexes(self):
        return []

class GhostIndexableAdapter(IndexableAdapter):

    grok.context(interfaces.IGhost)

    def getIndexes(self):
        if self.context == None:
            return []
        version = self.context.get_viewable()
        if version is None:
            return []
        else:
            haunted = version.get_haunted()
            if not haunted:
                return []
        return interfaces.IIndexable(haunted).getIndexes()

class ContainerIndexableAdapter(IndexableAdapter):

    grok.context(interfaces.IContainer)

    def getIndexes(self):
        index = self.context.index
        return interfaces.IIndexable(index).getIndexes()
