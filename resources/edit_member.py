view = context
request = view.REQUEST

view.get_root().security_trigger()
userid = request.AUTHENTICATED_USER.getId()

member = view.service_members.get_member(userid)
return getattr(view.Members, member.id).edit['tab_edit']()
