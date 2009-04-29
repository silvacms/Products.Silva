## Script (Python) "download_xml"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
RESPONSE = context.REQUEST.RESPONSE
model = context.REQUEST.model
data = model.get_zip(with_sub_publications, export_last_version)

RESPONSE.setHeader('Content-Type', 'application/zip')
RESPONSE.setHeader('Content-Length', len(data))
# RESPONSE.setHeader(
#     'Content-Disposition',
#     'inline; filename=%s.zip' % model.id)

RESPONSE.setHeader('Content-Disposition',
		   'attachment;filename=%s.zip' % model.id)

return data
