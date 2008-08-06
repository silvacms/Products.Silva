
from grokcore import component

from Products.Silva import interfaces as silva_interfaces
from Products.Silva.adapters import interfaces

class IndexableAdapter(component.Adapter):
    component.context(silva_interfaces.ISilvaObject)
    component.implements(interfaces.IIndexable)

    def __init__(self, context):
        self.context = context
        
    def getTitle(self):
        return self.context.get_title()

    def getPath(self):
        return self.context.getPhysicalPath()

    def getIndexes(self):
        return [] 

class GhostIndexableAdapter(IndexableAdapter):
    component.context(silva_interfaces.IGhost)
    
    def getIndexes(self):
        if self.context == None:
            return []
        version = self.context.get_viewable()
        if version is None:
            return []
        else:
            haunted = version.get_haunted_unrestricted()
            if not haunted:
                return []
        return interfaces.IIndexable(haunted).getIndexes()

class ContainerIndexableAdapter(IndexableAdapter):
    component.context(silva_interfaces.IContainer)
    
    def getIndexes(self):
        index = self.context.index
        return interfaces.IIndexable(index).getIndexes() 
