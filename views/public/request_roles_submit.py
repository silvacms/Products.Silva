from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
userid = request.AUTHENTICATED_USER.getId()

if not request.has_key('roles') or not request['roles']:
    return context.request_roles(message=_('No roles were selected.'))

member = None
if request.has_key('fullname') or request.has_key('email'):
    if not request['fullname'] or not request['email']:
        return context.request_roles(message=_('You must enter your full name and your e-mail address'))
    member = context.service_members.get_member(userid)
    member.set_fullname(request['fullname'])
    member.set_email(request['email'])

try:
    model.request_roles_for_user(request.AUTHENTICATED_USER.getId(), request['roles'])
except Exception, e:
    msg = _('Error: ${error}', mapping={'error': e})
    return context.request_roles(message=msg)
else:
    return context.service_resources.Silva.request_processed(message=_('Roles requested. You will receive an e-mail from the Chief Editor or Manager as soon as your request is processed.'), last_url=request['last_url'])
