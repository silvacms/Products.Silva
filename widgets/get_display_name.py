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
name = wr.getDisplayName(node.nodeName)
if same_type(name, u' '):
  name = node.output_convert_editable(name)
return name
