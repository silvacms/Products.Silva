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
retval = ''
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'dt':
        retval += editorsupport.render_text_as_editable(child).strip() + \
            '\r\n'
    elif child.nodeName == 'dd':
        retval += editorsupport.render_text_as_editable(child).strip() + \
            '\r\n\r\n'

return retval
