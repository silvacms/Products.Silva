## Script (Python) "add_groups_to_virtual_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=group=None, virtual_groups=None
##title=
##
request = context.REQUEST
model = request.model
view = context

if not group:
    return view.tab_access_groups(message_type="error", message="No group selected.")
if not virtual_groups:
    return view.tab_access_groups(message_type="error", message="No virtual groups selected.")

mapping = model#.sec_get_or_create_groupsmapping()
groups_added = []
for virtual_group in virtual_groups:
    mapping.addGroupToVirtualGroup(group, virtual_group)
    groups_added.append((group, virtual_group))

return view.tab_access_groups(
    message_type='feedback', 
    message='Added groups to virtual groups: %s' % view.quotify_list_ext(groups_added))
