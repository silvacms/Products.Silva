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
model = request.model

if not request.has_key('storageids') or not request['storageids']:
    return view.tab_edit_import(message_type='error', message='Select one or more jobs to import')

errors = []
for item in request['storageids']:
    sid, doctype = item.split('|')
    try:
        data = model.service_docma.get_finished_job(str(request['AUTHENTICATED_USER']), int(sid))
    except Exception, e:
        errors.append(e)
    else:
        if doctype == 'silva':
            try:
                model.xml_import(data)
            except Exception, e:
                errors.append('<<%s>> - %s' % (sid, e))
        else:
            model.manage_addProduct['Silva'].manage_addFile('doc_%s.doc' % sid, 'Docma Word Document %s' % sid, data)

if errors:
    return view.tab_edit_import(message_type='error', message='The following errors have occured during import: %s' % ', '.join(errors))
else:
    return view.tab_edit_import(message_type='feedback', message='Finished importing')
