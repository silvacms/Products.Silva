view = context
request = view.REQUEST

if not request['password']:
    return view.become_visitor(message="Enter a password")

if not request['password'] == request['password_retyped']:
    return view.become_visitor(message="Passwords don't match")

if not request['username']:
    return view.become_visitor(message="Enter a username")

if not view.is_userid_available(request['username']):
    return view.become_visitor(message='Username already in use')

# add user to the site
view.add_user(request['username'], request['password'])

# add a memberobject by getting it (the class will create it)
member = view.service_members.get_member(request['username'])

return view.service_resources.Silva.request_processed(message="You are now a registered user. Your username is '%s'. Write down your username and password so you won't forget them!" % request['username'])
