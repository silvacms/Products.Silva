##parameters=userids=None
model = context.REQUEST.model
view = context

if userids is None:
    return view.tab_access_lookup(
        message_type="error", message="No users selected.")

selection = view.lookup_get_selection()
for userid in userids:
    member = model.sec_get_member(userid)
    if member is None:
        continue
    selection[userid] = 1

return view.tab_access_lookup(
    message_type="feedback", 
    message="Users selected.")
