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
editorsupport = context.service_editorsupport
items = []
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'li':
        items.append(editorsupport.render_text_as_editable(child))
import string
items = map(string.strip, items)
return '\r\n\r\n'.join(items)
