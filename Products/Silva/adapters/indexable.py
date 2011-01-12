# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core import interfaces


class IndexableAdapter(grok.Adapter):
    grok.implements(interfaces.IIndexEntries)
    grok.context(interfaces.ISilvaObject)

    def get_title(self):
        return self.context.get_title()

    def get_entries(self):
        return []


class GhostIndexableAdapter(IndexableAdapter):
    grok.context(interfaces.IGhost)

    def get_entries(self):
        if self.context == None:
            return []
        version = self.context.get_viewable()
        if version is None:
            return []
        else:
            haunted = version.get_haunted()
            if not haunted:
                return []
        return interfaces.IIndexEntries(haunted).get_entries()


class ContainerIndexableAdapter(IndexableAdapter):
    grok.context(interfaces.IContainer)

    def get_entries(self):
        index = self.context.index
        return interfaces.IIndexEntries(index).get_entries()
