## Script (Python) "save_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
row = request.node
editorsupport = context.service_editorsupport
node = row.firstChild
while node:
    is_simple = context.is_field_simple(node)
    if not is_simple:
        node = node.nextSibling
        continue
    p_node = node.firstChild
    data = request[p_node.getNodePath('widget')]
    editorsupport.replace_text(p_node, data)
    node = node.nextSibling
    
