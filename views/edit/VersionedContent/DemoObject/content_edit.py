## Script (Python) "content_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
editable = model.get_editable()
request = context.REQUEST

request.set(
    'xml_url',
    model.absolute_url() + '/' + model.get_unapproved_version() + '/content')
request.set('xml_rel_url', model.get_unapproved_version() + '/content')

service_editor = context.service_editor
service_editor.setDocumentEditor(editable.content.documentElement,
                                 'service_field_editor')
return service_editor.render(
    service_editor.getRoot(editable.content.documentElement))
