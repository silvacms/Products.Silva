## Script (Python) "get_display_name"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=wr_name, node
##title=
##
wr = getattr(context, wr_name)
return wr.getDisplayName(node.nodeName)
