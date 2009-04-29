##parameters=groups=[]
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

if not groups:
    return context.tab_edit(
        message_type="error",
        message=_("No group selected, so nothing copied."))

copied = model.copyIPRangesFromIPGroups(groups)
if copied:
    message = _("Range(s) ${copied} added.",
                mapping={'copied': context.quotify_list(copied)})
    type = 'feedback'
else:
    message = _("Nothing copied.")
    type = 'error'
return context.tab_edit(message_type=type, message=message)

