## Script (Python) "get_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=version
##title=
##
context.service_editor.setViewer('service_field_viewer')
return context.service_editor.getViewer().getWidget(version.content.documentElement).render()
