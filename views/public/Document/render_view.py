## Script (Python) "render_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
version = model.get_viewable()
if version is None:
   return "Sorry, this document is not published yet."
node = version.content.documentElement
context.service_editor.setViewer('service_doc_viewer')
return context.service_editor.renderView(node)
