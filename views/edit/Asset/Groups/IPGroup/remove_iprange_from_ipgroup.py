##parameters=ipranges=[]
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

if not ipranges:
    return context.tab_edit(
        message_type="error",
        message=_("No ip ranges were selected, so nothing was removed."))
removed = []
for iprange in ipranges:
    model.removeIPRange(iprange)
    removed.append(iprange)
removed = context.quotify_list(removed)
message = _("Range(s) ${removed} removed from the group.",
            mapping={'removed': removed})
return context.tab_edit(message_type="feedback", message=message)

