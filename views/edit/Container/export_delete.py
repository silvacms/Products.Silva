## Script (Python) "export_delete.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=delete_after_import=0
##title=
##
"""delete a job from the docma queue"""
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

model.security_trigger()

if not request.has_key('storageids') or not request['storageids']:
    return context.tab_status_export(message_type='error', message=_('Select one or more jobs to delete'))

for item in request['storageids']:
    sid, doctype = item.split('|')
    model.service_docma.delete_finished_job(str(request['AUTHENTICATED_USER']), int(sid))

return context.tab_status_export(message_type='feedback', message=_('Job deleted'))

