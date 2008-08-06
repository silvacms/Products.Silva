
from grokcore import component

from Products.Silva.adapters import interfaces
from Products.Silva import interfaces as silva_interfaces

class IndexableBase(component.Adapter):

    component.context(silva_interfaces.IPublishable)
    component.implements(interfaces.ICatalogIndexable)

    def __init__(self, context):
        self.context = context

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

    component.context(silva_interfaces.IVersionedContent)
    
    def index(self):
        self.context.indexVersions()

    def unindex(self):
        self.context.unindexVersions()

    
class SimpleIndexable(IndexableBase):
    """Index non-versioned content, such as folders and simple content,
    and assets.
    """

    component.context(silva_interfaces.IAsset)
    
    def index(self):
        self.context.index_object()

    def unindex(self):
        self.context.unindex_object()

    def reindex(self):
        self.context.reindex_object()

