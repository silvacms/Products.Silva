##parameters=groupids=None

request = context.REQUEST
model = request.model
view = context

if not groupids:
    return view.tab_edit(
        message_type="error", 
        message="No groups selected, so none removed.")

removed = []
for groupid in groupids:
    model.removeGroup(groupid)
    removed.append(groupid)

return view.tab_edit(
    message_type="feedback", 
    message="Group(s) %s removed from group." % view.quotify_list(removed))

