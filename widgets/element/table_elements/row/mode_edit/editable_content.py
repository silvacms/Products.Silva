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
texts = [render_field(node=child) for child in node.childNodes 
         if child.nodeType == node.ELEMENT_NODE]
return ''.join(texts)
