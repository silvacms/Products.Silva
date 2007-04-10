##parameters=groups=None
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

groupids = {}

if not groups:
    return view.tab_edit(
        message_type="error", 
        message=_("No group(s) selected, so nothing to use to add groups."))

added = model.copyGroupsFromVirtualGroups(groups)
if added:
    message = _("Group(s) ${added} added to group.",
                mapping={'added': view.quotify_list(added)})
else:
    message = _(
        "No other groups added (were they already in this virtual group?)")

return view.tab_edit(
    message_type="feedback", 
    message=message)
