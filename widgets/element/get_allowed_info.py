## Script (Python) "get_allowed_info"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=wr_name, node
##title=
##
wr = getattr(context, wr_name)
return [(wr.getDisplayName(name).capitalize(), name)
        for name in wr.getAllowed(node.parentNode.nodeName)]
