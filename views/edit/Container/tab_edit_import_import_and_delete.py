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

refresh_page = 'tab_edit_import'
if request.has_key('refresh_page') and request['refresh_page']:
    refresh_page = request['refresh_page']

refresh_page = getattr(view, refresh_page)

model.security_trigger()

if not request.has_key('storageids') or not request['storageids']:
    return refresh_page(message_type='error', message='Select one or more jobs to import')

errors = []
for item in request['storageids']:
    sid, doctype = item.split('|')
    data = model.service_docma.get_finished_job(str(request['AUTHENTICATED_USER']), int(sid))
    if doctype == 'silva':
        try:
            model.xml_import(data)
        except Exception, e:
            errors.append('<<%s>> - %s' % (sid, e))
        else:
            model.service_docma.delete_finished_job(str(request['AUTHENTICATED_USER']), int(sid))
    else:
        newid = 'doc_%s.doc' % sid
        while hasattr(model, newid):
            newid = 'copy_of_%s' % newid
        try:
            model.manage_addProduct['Silva'].manage_addFile(newid, 'Docma Word Document %s' % sid, data)
        except:
            return refresh_page(message_type='error', message='Could not import %s' % newid)
        else:
            model.service_docma.delete_finished_job(str(request['AUTHENTICATED_USER']), int(sid))

if errors:
    return refresh_page(message_type='error', message='The following errors have occured: %s' % ', '.join(errors))
else:
    return refresh_page(message_type='feedback', message='Finished')
