## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.service_editor.setViewer("service_ntable_viewer")
return context.service_editor.getViewer().getWidget(context.REQUEST.node).render()
