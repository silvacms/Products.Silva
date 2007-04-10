## Script (Python) "tab_status_silva2word"
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
model = request.model

# if we don't call security_trigger here, the script will be called twice and the job will be started twice
model.security_trigger()

if not request.has_key('refs') or not request['refs']:
    return view.tab_status(message_type='error', message=_('No items were selected, so nothing is exported'))

objects = []
for ref in request['refs'].split('||'):
    objects.append(model.resolve_ref(ref.strip()))

# turn refs inot a list so tab_status_export can re-use it the refs from the request
request.set('refs', request['refs'].split('||'))

if request.has_key('with_sub_publications') and request['with_sub_publications']:
    with_sub_publications = 1

if request.has_key('export_last_version') and request['export_last_version']:
    export_last_version = 1

description = _('No description')
if request.has_key('description') and request['description']:
    description = request['description']

data = model.get_xml_for_objects(objects, with_sub_publications, export_last_version)

if not request['email']:
    return view.tab_status(message_type='error', message=_('You have not entered your e-mail address'))

ident, status = model.service_docma.silva2word(request['email'], data, request['template'], str(request.AUTHENTICATED_USER.getId()), description)

msg = _('Your job is ${status}. The id of your job is ${job_id}.',
        mapping={'status': status, 'job_id': ident})
return view.tab_status_export(message_type='feedback', message=msg)
