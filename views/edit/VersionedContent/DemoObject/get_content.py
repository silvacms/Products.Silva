## Script (Python) "get_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
version = model.get_editable()
context.service_editor.setViewer('service_field_viewer')
return context.service_editor.getViewer().getWidget(version.content.documentElement).render()
