from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

class Index:
    def __init__(self, name):
        self.name = name

class IndexableAdapter(adapter.Adapter):
    """
    """
    __implements__ = (interfaces.IIndexable,)

    def __init__(self, context):
        adapter.Adapter.__init__(self, context)

    def getIndexes(self):
        indexes = []
        for version in self.context.get_indexables():
            docElement = version.content.firstChild
            nodes = docElement.getElementsByTagName('index')
            for node in nodes:
                index = Index(node.getAttribute('name'))
                indexes.append(index)
        return indexes or None

def getIndexableAdapter(context):
    return IndexableAdapter(context).__of__(context)

