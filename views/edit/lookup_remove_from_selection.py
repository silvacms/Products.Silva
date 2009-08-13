##parameters=userids=None
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context

def return_results(message_type,message):
    if not model.sec_can_find_users():
        return view.lookup_ui(message_type=message_type, message=message)
    else:
        return view.lookup_ui_direct(message_type=message_type, message=message)

if userids is None:
    return return_results(
        message_type="error", message=_("No users removed."))

selection = view.lookup_get_selection()
for userid in userids:
    if selection.has_key(userid): 
        del selection[userid]

return return_results(
    message_type="feedback", 
    message=_("Users removed from selection."))
