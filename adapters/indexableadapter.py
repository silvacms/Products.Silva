from zope.interface import implements

from Products.Silva.interfaces import IContent, IGhost, IContainer
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

class IndexableAdapter(adapter.Adapter):
    """
    """
    implements(interfaces.IIndexable)

    def getTitle(self):
        return self.getContext().get_title()

    def getPath(self):
        return self.getContext().getPhysicalPath()

    def getIndexes(self):
        return [] 

class DocumentIndexesAdapter(IndexableAdapter):
    def getIndexes(self):
        version = self.getContext().get_viewable()
        if version is None:
            return []
        indexes = []
        docElement = version.content.firstChild
        nodes = docElement.getElementsByTagName('index')
        for node in nodes:
            indexName = node.getAttribute('name')
            indexes.append(indexName)
        return indexes

class GhostIndexesAdapter(IndexableAdapter):
    def getIndexes(self):
        if self.getContext() == None:
            return []
        version = self.getContext().get_viewable()
        if version is None:
            return []
        else:
            haunted = version.get_haunted_unrestricted()
            if not haunted:
                return []
        return getIndexableAdapter(haunted).getIndexes()

class ContainerIndexesAdapter(IndexableAdapter):
    def getIndexes(self):
        index = self.getContext().index
        return getIndexableAdapter(index).getIndexes() 

def getIndexableAdapter(context):
    if context.meta_type == "Silva Document":
        return DocumentIndexesAdapter(context).__of__(context)

    if IGhost.providedBy(context): 
        return GhostIndexesAdapter(context).__of__(context) 

    if IContainer.providedBy(context):
        return ContainerIndexesAdapter(context).__of__(context) 
    
    return IndexableAdapter(context).__of__(context)
