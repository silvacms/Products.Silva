## Script (Python) "simple_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node
##title=
##
editorsupport = context.service_editorsupport
for child in node.childNodes:
    if child.nodeType == node.ELEMENT_NODE:
        break
content = node.get_content()
return editorsupport.render_text_as_editable(child)
