## Script (Python) "download_xml"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
RESPONSE = context.REQUEST.RESPONSE
model = request.model
docmapdf = context.service_docmapdf

from DateTime import DateTime

if not request.has_key('refs') or not request['refs']:
    return context.tab_status(message_type='error', message=_('No items were selected, so no content will be exported'))

objects = []
for ref in request['refs'].split('||'):
    objects.append(model.resolve_ref(ref))

ss = docmapdf.active_stylesheet
xml_data = model.get_xml_for_objects(objects, with_sub_publications, export_last_version)
pdf_data = docmapdf.manage_generatePDF(xml_data, ss)
filename = '%s_export_%s.pdf' % (model.id, DateTime().strftime('%Y-%m-%d'))
RESPONSE.setHeader('content-type', 'application/pdf')
RESPONSE.setHeader('content-disposition', 'attachment;filename=%s'%filename)

return pdf_data
