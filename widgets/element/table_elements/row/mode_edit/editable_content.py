## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
render_field = context.render_editable_field

child_nodes = [child for child in node.childNodes 
               if child.nodeType == node.ELEMENT_NODE]

if not child_nodes:
    return ''

cellwidth = '%s%%' % int(1.0/len(child_nodes) * 100)
texts = [render_field(node=child, cellwidth=cellwidth) for child in child_nodes]
return ''.join(texts)
