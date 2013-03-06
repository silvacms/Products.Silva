# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IIndexEntries
from silva.core.interfaces import ISilvaObject, IGhost, IContainer


class IndexableAdapter(grok.Adapter):
    grok.implements(IIndexEntries)
    grok.provides(IIndexEntries)
    grok.context(ISilvaObject)

    def get_title(self):
        return self.context.get_title()

    def get_entries(self):
        return []


class GhostIndexableAdapter(IndexableAdapter):
    grok.context(IGhost)

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
        return IIndexEntries(haunted).get_entries()


class ContainerIndexableAdapter(IndexableAdapter):
    grok.context(IContainer)

    def get_entries(self):
        default = self.context.get_default()
        if default is not None:
            return IIndexEntries(default).get_entries()
        return []
