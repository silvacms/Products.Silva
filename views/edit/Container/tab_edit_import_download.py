## Script (Python) "tab_docma_import"
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
response = view.REQUEST.RESPONSE
model = request.model

if not request.has_key('storageids') or not request['storageids']:
    return view.tab_edit_import(message_type='error', message='Select one or more items to download')

errors = []
for item in request['storageids']:
    sid, doctype = item.split('|')
    data = model.service_docma.get_finished_job(str(request['AUTHENTICATED_USER']), int(sid))
    filename = 'download_%s' % sid
    if doctype == 'silva':
        filename += '.slv'
    else:
        filename += '.doc'

response.setHeader('Content-Type', 'application/download')
response.setHeader('Content-Length', len(data))
response.setHeader('Content-Disposition',
                   'attachment;filename=%s' % filename)

return data