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
doc = node.ownerDocument
p = doc.createElement('p')
p.appendChild(doc.createTextNode(''))
node.appendChild(p)
