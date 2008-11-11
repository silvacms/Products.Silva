## Script (Python) "tab_edit_word2silva"
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
model = request.model

model.security_trigger()

if not request.has_key('importfile') or not request['importfile']:
    return context.tab_edit_import(message_type='error', message=_('Select a file for upload'))

if not request.has_key('email') or not request['email']:
    return context.tab_edit_import(message_type='error', message=_('You must enter your e-mail address'))

description = request['importfile'].filename
if request.has_key('description') and request['description']:
    description = request['description']

data = request['importfile'].read()

ident, status = model.service_docma.word2silva(data, str(request.AUTHENTICATED_USER), request['email'], description)

message = _('Your job is ${status}. The id of your job is ${id}.',
            mapping={'status': status, 'id': ident})
return context.tab_edit_import(message_type='feedback', message=message)
