##parameters=userids=None

request = context.REQUEST
model = request.model
view = context

if not userids:
    return view.tab_access(
        message_type="error", message="No users selected, so none added.")

added = []
current_users = model.listUsers()
for userid in userids:
    if not userid in current_users:
        model.addUser(userid)
        added.append(userid)

if added:
    message = "User(s) %s added to group." % view.quotify_list(added)
else:
    message = "No other users added (were they already in this group?)"

return view.tab_edit(
    message_type="feedback", 
    message=message)

