## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
editorsupport = context.service_editorsupport
#columns = int(node.parentNode.getAttribute('columns'))

for child in tuple(node.childNodes):
   if child.nodeType != node.ELEMENT_NODE:
       continue
   try:
       # find p
       for p_node in child.childNodes:
           if p_node.nodeType == node.ELEMENT_NODE:
               break
       data = context.REQUEST[p_node.getNodePath('widget')]
       editorsupport.replace_text(p_node, data)
   except KeyError:
       pass
