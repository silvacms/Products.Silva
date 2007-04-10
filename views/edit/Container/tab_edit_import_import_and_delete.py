## Script (Python) "tab_docma_import_and_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=delete_after_import=0
##title=
##
from Products.Silva.i18n import translate as _

view = context
request = view.REQUEST
model = request.model

model.security_trigger()

if not request.has_key('storageids') or not request['storageids']:
    return view.tab_edit_import(message_type='error', message=_('Select one or more jobs to import'))

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
            message = _('Could not import ${newid}', mapping={'newid': newid})
            return view.tab_edit_import(message_type='error', message=message)
        else:
            model.service_docma.delete_finished_job(str(request['AUTHENTICATED_USER']), int(sid))

if errors:
    message = _('The following errors have occured during import: ${errors}',
                mapping={'errors': ', '.join(errors)})
    return view.tab_edit_import(message_type='error', message=message)
else:
    return view.tab_edit_import(message_type='feedback', message=_('Finished importing'))
