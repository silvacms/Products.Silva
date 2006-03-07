##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
from Products.Silva.i18n import translate as _

view = context
request = view.REQUEST
RESPONSE = view.REQUEST.RESPONSE
model = request.model

from DateTime import DateTime

if not request.has_key('refs') or not request['refs']:
    return view.tab_status(
        message_type='error', 
        message=_('No items were selected, so no content will be exported'))

refs = request['refs'].split('||')

if len(refs) > 1:
    return view.tab_status(
        message_type='error', message=_(
            'Currently, fullmedia export only supports one item at a time.'))

object = model.resolve_ref(refs[0])

#raise repr(export_last_version)
data = object.get_zip(with_sub_publications, export_last_version)

filename = object.id
RESPONSE.setHeader('Content-Type', 'application/download')
RESPONSE.setHeader('Content-Length', len(data))
RESPONSE.setHeader(
    'Content-Disposition', 'attachment;filename=%s_export_%s.zip' % (
    filename, DateTime().strftime('%Y-%m-%d')))

return data
