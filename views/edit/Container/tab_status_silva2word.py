## Script (Python) "tab_status_silva2word"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=with_sub_publications=0, export_last_version=0
##title=
##
view = context
request = view.REQUEST
model = request.model

if request.has_key('with_sub_publications') and request['with_sub_publications']:
    with_sub_publications = 1

if request.has_key('export_last_version') and request['export_last_version']:
    export_last_version = 1

outfilename = 'silva_export.doc'
if request.has_key('outfilename') and request['outfilename']:
    outfilename = request['outfilename']

data = model.get_xml(with_sub_publications, export_last_version)

if not request['email_address']:
    return view.tab_status(message_type='error', message='You have not entered your e-mail address')

ident, status = model.service_docma.silva2word('guido@infrae.com', data, request['template'], outfilename, request.AUTHENTICATED_USER.getId())

return view.tab_status_export(message_type='feedback', message='Your job is %s. The id of your job is %s.' % (status, ident))
