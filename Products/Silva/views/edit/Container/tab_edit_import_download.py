## Script (Python) "tab_docma_import"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=delete_after_import=0
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
response = context.REQUEST.RESPONSE
model = request.model

if not request.has_key('storageid') or not request['storageid']:
    return context.tab_edit_import(message_type='error', message=_('Select one or more items to download'))

errors = []
sid, doctype = request['storageid'].split('|')
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
