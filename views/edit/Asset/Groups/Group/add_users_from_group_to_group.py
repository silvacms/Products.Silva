##parameters=groups=None

request = context.REQUEST
model = request.model
view = context

userids = {}

if not groups:
    return view.tab_edit(
        message_type="error", 
        message="No group(s) selected, so nothing to use to add users.")

added = model.copyUsersFromGroups(groups)
if added:
    message = "User(s) %s added to group." % view.quotify_list(added)
else:
    message = "No other users added (were they already in this group?)"

return view.tab_edit(
    message_type="feedback", 
    message=message)

