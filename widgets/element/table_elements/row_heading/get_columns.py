## Script (Python) "get_columns"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
return int(node.parentNode.getAttribute('columns'))
