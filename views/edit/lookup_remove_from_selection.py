##parameters=userids=None
from Products.Silva.i18n import translate as _

model = context.REQUEST.model

if userids is None:
    return context.lookup_ui(
        message_type="error", message=_("No users removed."))

selection = context.lookup_get_selection()
for userid in userids:
    if selection.has_key(userid):
        del selection[userid]

return context.lookup_ui(
    message_type="feedback",
    message=_("Users removed from selection."))
