view = context
request = view.REQUEST
model = request.model
userid = request.AUTHENTICATED_USER.getId()

if not request.has_key('roles') or not request['roles']:
    return view.request_roles(message='No roles were selected.')

member = None
if request.has_key('fullname') or request.has_key('email'):
    if not request['fullname'] or not request['email']:
        return view.request_roles(message='You must enter your full name and your e-mail address')
    member = view.service_members.get_member(userid)
    member.set_fullname(request['fullname'])
    member.set_email(request['email'])

try:
    model.request_roles_for_user(request.AUTHENTICATED_USER.getId(), request['roles'])
except Exception, e:
    return view.request_roles(message='Error: %s' % e)
else:
    return view.service_resources.Silva.request_processed(message='Roles requested. You will receive an e-mail from the Chief Editor or Manager as soon as your request is processed.')
