## Script (Python) "access_assign_to_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groups=None, assign_role=None
##title=
##
view = context
model = context.REQUEST.model

if not assign_role or assign_role == 'None':
    return view.tab_access(message_type="error", message="No role selected.")
if not groups:
    return view.tab_access(message_type="error", message="No groups selected.")

# get mapping object
map = model.sec_get_or_create_groupsmapping()
assigned = []
for group in groups:
    map.assignRolesToGroup(group, [assign_role])
    assigned.append((group, assign_role))

return view.tab_access(
    message_type="feedback", 
    message="Role(s) assigned for %s" % view.quotify_list_ext(assigned))
