##parameters=groups=None

request = context.REQUEST
model = request.model
view = context

groupids = {}

if not groups:
    return view.tab_edit(
        message_type="error", 
        message="No group(s) selected, so nothing to use to add groups.")

added = model.copyGroupsFromVirtualGroups(groups)
if added:
    message = "Group(s) %s added to group." % view.quotify_list(added)
else:
    message = "No other groups added (were they already in this virtual group?)"

return view.tab_edit(
    message_type="feedback", 
    message=message)
