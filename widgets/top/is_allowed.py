## Script (Python) "is_allowed"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=wr_name, node, name
##title=
##
wr = getattr(context, wr_name)
return wr.isAllowed(node.nodeName, name)
