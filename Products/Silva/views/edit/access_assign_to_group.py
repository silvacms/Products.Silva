## Script (Python) "access_assign_to_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groups=None, assign_group_role=None
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
assign_role = assign_group_role

if not assign_group_role or assign_role == 'None':
    return context.tab_access(message_type="error", message=_("No role selected."))
if not groups:
    return context.tab_access(message_type="error", message=_("No groups selected."))

# get mapping object
map = model.sec_get_or_create_groupsmapping()
assigned = []
for group in groups:
    group = unicode(group, 'UTF-8')
    map.assignRolesToGroup(group, [assign_role])
    assigned.append((group, assign_role))

msg = _("Role(s) assigned for ${list}",
        mapping={'list': context.quotify_list_ext(assigned)})
return context.tab_access(
    message_type="feedback",
    message=msg)
