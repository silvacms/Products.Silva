view = context
request = view.REQUEST
userid = request.AUTHENTICATED_USER.getId()

if not request['roles']:
    return view.request_roles(message='No roles selected!')

member = None
if request.has_key('fullname') or request.has_key('email'):
    if not request['fullname'] or not request['email']:
        return view.request_roles(message='You must enter your full name and your e-mail address')
    member = view.service_members.get_member_object(userid)
    member.set_fullname(request['fullname'])
    member.set_email(request['email'])

context.request_roles_for_user(request.AUTHENTICATED_USER.getId(), request['roles'])

return view.request_processed(message='Roles requested. You will receive an e-mail from the chief-editor or manager as soon as your request is processed.')
