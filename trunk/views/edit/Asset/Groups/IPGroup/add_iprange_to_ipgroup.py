##parameters=iprange
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

if not iprange:
    return context.tab_edit(
        message_type="error",
        message=_("No ip range was provided, so nothing was added.")
        )

try:
    model.addIPRange(iprange)
except ValueError, e:
    message = str(e)
    type = 'error'
else:
    message = _("Range ${iprange} added to the IP Group",
                mapping={'iprange': context.quotify(iprange)})
    type = 'feedback'
return context.tab_edit(message_type=type, message=message)

