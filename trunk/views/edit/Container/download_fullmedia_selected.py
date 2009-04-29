##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=export_format='zip',with_sub_publications=0, export_last_version=0
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
RESPONSE = context.REQUEST.RESPONSE
model = request.model

from DateTime import DateTime

if not request.has_key('refs') or not request['refs']:
    return context.tab_status(
        message_type='error',
        message=_('No items were selected, so no content will be exported'))

refs = request['refs'].split('||')

if len(refs) > 1:
    return context.tab_status(
        message_type='error', message=_(
            'Currently, fullmedia export only supports one item at a time.'))

object = model.resolve_ref(refs[0])

data = object.export_content(export_format,
                             with_sub_publications,
                             export_last_version)

filename = object.id
RESPONSE.setHeader('Content-Type', 'application/download')
RESPONSE.setHeader('Content-Length', len(data))
RESPONSE.setHeader(
    'Content-Disposition', 'attachment;filename=%s_export_%s.%s' % (
    filename,
    DateTime().strftime('%Y-%m-%d'),
    export_format))

return data
