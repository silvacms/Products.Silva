## Script (Python) "tab_docma_import_and_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=delete_after_import=0
##title=
##
view = context
request = view.REQUEST
model = request.model

if not request.has_key('storageids') or not request['storageids']:
    return view.tab_docma(message_type='error', message='Select one or more jobs to delete')

for sid in request['storageids']:
    xml = model.service_docma.get_finished_w2s_job(str(request['AUTHENTICATED_USER']), int(sid))
    model.service_docma.delete_finished_job(str(request['AUTHENTICATED_USER']), int(sid))

return view.tab_docma(message_type='feedback', message='Finished importing deleting')
