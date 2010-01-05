# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core import interfaces

class IndexableBase(grok.Adapter):

    grok.implements(interfaces.ICatalogIndexable)
    grok.context(interfaces.IPublishable)

    def index(self):
        raise NotImplementedError

    def unindex(self):
        raise NotImplementedError
    
    def reindex(self):
        self.unindex()
        self.index()

class VersionedContentIndexable(IndexableBase):
    """Index versioned content.
    """

    grok.context(interfaces.IVersionedContent)
    
    def index(self):
        self.context.indexVersions()

    def unindex(self):
        self.context.unindexVersions()

    
class SimpleIndexable(IndexableBase):
    """Index non-versioned content, such as folders and simple content,
    and assets.
    """

    grok.context(interfaces.IAsset)
    
    def index(self):
        self.context.index_object()

    def unindex(self):
        self.context.unindex_object()

    def reindex(self):
        self.context.reindex_object()

