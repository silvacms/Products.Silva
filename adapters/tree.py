from Products.Silva.interfaces import IContent, IGhost, IContainer
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

class TreeNode(adapter.Adapter):
    __implements__ = (interfaces.ITreeNode,)
    
    def getObject(self):
        return self.context

    def getChildNodes(self):
        for object in []:
            yield object

class ContainerTreeNode(TreeNode):
    def getChildNodes(self):
        for obj in self.context.get_ordered_publishables():
            yield getTreeNodeAdapter(obj)

def getTreeNodeAdapter(context):
    if IContainer.isImplementedBy(context):
        return ContainerTreeNode(context).__of__(context) 
    return TreeNode(context).__of__(context)
