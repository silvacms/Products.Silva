##parameters=userids=None
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

if not userids:
    return view.tab_edit(
        message_type="error", 
        message=_("No users selected, so none removed.")
        )

removed = []
for userid in userids:
    model.removeUser(userid)
    removed.append(userid)

message = _("User(s) ${removed} removed from group.",
            mapping={'removed': view.quotify_list(removed)})
return view.tab_edit(
    message_type="feedback", 
    message=message
    )

