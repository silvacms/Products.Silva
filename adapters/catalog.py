from zope.interface import implements
from interfaces import ICatalogIndexable

class IndexableBase(object):
    implements(ICatalogIndexable)

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
    def index(self):
        self.context.indexVersions()

    def unindex(self):
        self.context.unindexVersions()
    
class SimpleIndexable(IndexableBase):
    """Index non-versioned content, such as folders and simple content,
    and assets.
    """
    def index(self):
        self.context.index_object()

    def unindex(self):
        self.context.unindex_object()

    def reindex(self):
        self.context.reindex_object()

