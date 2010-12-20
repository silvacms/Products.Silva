##parameters=userids=None
from Products.Silva.i18n import translate as _

model = context.REQUEST.model

if userids is None:
    return context.lookup_ui(
        message_type="error", message=_("No users selected."))

selection = context.lookup_get_selection()
for userid in userids:
    member = model.sec_get_member(userid)
    if member is None:
        continue
    selection[userid] = 1

return context.lookup_ui(
    message_type="feedback",
    message=_("Users selected."))
