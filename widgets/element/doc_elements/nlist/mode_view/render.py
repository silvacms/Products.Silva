## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
context.service_editor.setViewer('service_nlist_viewer')
return context.service_editor.renderView(node)
