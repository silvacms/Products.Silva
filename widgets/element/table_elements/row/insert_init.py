## Script (Python) "insert_init"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
columns = int(node.parentNode.getAttribute('columns'))
doc = node.ownerDocument
for i in range(columns):
    field = doc.createElement('field')
    p = doc.createElement('p')
    p.appendChild(doc.createTextNode(''))
    field.appendChild(p)
    node.appendChild(field)
