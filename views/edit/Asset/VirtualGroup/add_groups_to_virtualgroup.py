##parameters=groups=None

request = context.REQUEST
model = request.model
view = context

if not groups:
    return view.tab_edit(
        message_type="error", message="No groups selected, so none added.")

added = []
current_groups = model.listGroups()
for groupid in groups:
    if not groupid in current_groups:
        model.addGroup(groupid)
        added.append(groupid)

if added:
    message = "Group(s) %s added to group." % view.quotify_list(added)
else:
    message = "No other groups added (were they already in this virtual group?)"

return view.tab_edit(
    message_type="feedback", 
    message=message)

