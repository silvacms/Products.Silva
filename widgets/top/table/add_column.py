## Script (Python) "add_column"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
doc = node.ownerDocument
for row in node.childNodes:
    if row.nodeName != 'row':
        continue
    # add field
    field = doc.createElement('field')
    p = doc.createElement('p')
    p.appendChild(doc.createTextNode(''))
    field.appendChild(p)

    row.appendChild(field)

node.setAttribute(
    'columns', 
    node.input_convert(str(int(node.getAttribute('columns')) + 1)) )

if node.hasAttribute('column_info'):
    node.setAttribute('column_info', node.getAttribute('column_info') + u' L:1')

# invalidate cache
#for mode in ['mode_normal', 'mode_edit', 'mode_insert', 'mode_done']:
#    context.service_editor.invalidateCache(node,
#       ('service_document_editor_widgets', 'element', 'table', mode))

return context.redirect()
