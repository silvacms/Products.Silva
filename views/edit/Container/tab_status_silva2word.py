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

# if we don't call security_trigger here, the script will be called twice and the job will be started twice
model.security_trigger()

if request.has_key('with_sub_publications') and request['with_sub_publications']:
    with_sub_publications = 1

if request.has_key('export_last_version') and request['export_last_version']:
    export_last_version = 1

description = 'No description'
if request.has_key('description') and request['description']:
    description = request['description']

data = model.get_xml(with_sub_publications, export_last_version)

if not request['email']:
    return view.tab_status_export(message_type='error', message='You have not entered your e-mail address')

ident, status = model.service_docma.silva2word(request['email'], data, request['template'], str(request.AUTHENTICATED_USER.getId()), description)

return view.tab_status_export(message_type='feedback', message='Your job is %s. The id of your job is %s.' % (status, ident))
