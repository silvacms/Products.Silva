##parameters=userids=None

request = context.REQUEST
model = request.model
view = context

if not userids:
    return view.tab_edit(
        message_type="error", 
        message="No users selected, so none removed.")

removed = []
for userid in userids:
    model.removeUser(userid)
    removed.append(userid)

return view.tab_edit(
    message_type="feedback", 
    message="User(s) %s removed from group." % view.quotify_list(removed))

