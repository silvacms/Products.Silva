## Script (Python) "tab_edit_word2silva"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
view = context
request = view.REQUEST
model = request.model

if not request.has_key('importfile') or not request['importfile']:
    return view.tab_edit_import_docma(message_type='error', message='Select a file for upload')

data = request['importfile'].read()

ident, status = model.service_docma.word2silva(data, request.AUTHENTICATED_USER.getId(), model.getPhysicalPath())

return view.tab_edit_import_docma(message_type='feedback', message='Your job is %s. The id of your job is %s.' % (status, ident))
