## Script (Python) "remove_column"
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
columns = int(node.getAttribute('columns'))
if columns <= 1:
    # can't remove column if we only have one column left
    return

for row in node.childNodes:
    if row.nodeName != 'row':
        continue
    row.removeChild(row.lastChild)

# invalidate cache
#for mode in ['mode_normal', 'mode_edit', 'mode_insert', 'mode_done']:
#    context.service_editor.invalidateCache(node,
#       ('service_document_editor_widgets', 'element', 'table', mode))

node.setAttribute('columns', node.input_convert(str(columns - 1)))
if node.hasAttribute('column_info'):
    column_info = node.getAttribute('column_info').split()
    node.setAttribute('column_info', u' '.join(column_info[:-1]))

return context.redirect()
