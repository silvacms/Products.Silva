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
context.service_editor.setViewer('service_table_viewer')
viewer = context.service_editor.getViewer()
return viewer.getWidget(node).render()
