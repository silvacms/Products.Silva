##parameters=groupids=None
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

if not groupids:
    return view.tab_edit(
        message_type="error", 
        message=_("No groups selected, so none removed."))

removed = []
for groupid in groupids:
    model.removeGroup(groupid)
    removed.append(groupid)

message = _("Group(s) ${removed} removed from group.",
            mapping={'removed': view.quotify_list(removed)})
return view.tab_edit(
    message_type="feedback", 
    message=message)

