# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# Silva
from Products.Silva.interfaces import IContent, IGhost, IContainer
# Silva adapters
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces

class TreeNode(adapter.Adapter):
    
    __implements__ = (interfaces.ITreeNode,)
    
    def getObject(self):
        return self.context

    def getChildNodes(self):
        for i in []:
            yield i

class ContainerTreeNode(TreeNode):
    def getChildNodes(self):
        for obj in self.context.get_ordered_publishables():
            yield getTreeNodeAdapter(obj)

def getTreeNodeAdapter(context):
    if IContainer.isImplementedBy(context):
        return ContainerTreeNode(context).__of__(context) 
    return TreeNode(context).__of__(context)
