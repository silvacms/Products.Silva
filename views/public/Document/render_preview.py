## Script (Python) "render_preview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
version = model.get_previewable()
node = version.documentElement

context.service_editor.setViewer('service_doc_previewer')
return context.service_editor.getViewer().getWidget(node).render()
