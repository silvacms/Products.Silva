## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
columns_info = context.REQUEST['columns_info']
render_field = context.render_field
children = [child for child in node.childNodes if child.nodeType == node.ELEMENT_NODE]
result = []
for i in range(len(children)):
    result.append(render_field(children[i], columns_info[i]))
return ''.join(result)
