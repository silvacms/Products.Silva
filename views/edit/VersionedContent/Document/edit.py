## Script (Python) "edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
session = context.REQUEST.SESSION
model = context.REQUEST.model
editable = model.get_editable()

request = context.REQUEST
xml_url = (model.absolute_url() + '/' +
           model.get_unapproved_version() + '/content')
request.set('xml_url', xml_url)
request.set('xml_rel_url', '/%s/%s/content' % (
    model.absolute_url(1), model.get_unapproved_version()))

service_editor = context.service_editor
service_editor.setDocumentEditor(
    editable.content.documentElement,
    'service_doc_editor')

return service_editor.render(
    service_editor.getRoot(editable.content.documentElement))
