## Script (Python) "remove_groups_from_virtual_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groups_virtualgroups=None
##title=
##
request = context.REQUEST
model = request.model
view = context

if not groups_virtualgroups:
    return view.tab_access_groups(message_type="error", message="No groups selected.")

def extract_groups_virtual_groups(in_list):
    out_list = []
    for item in in_list:
        group, virtual_group = item.split('||')
        out_list.append((group, virtual_group))
    return out_list

mapping = model#.sec_get_groupsmapping()
groups_removed= []
for group, virtual_group in extract_groups_virtual_groups(groups_virtualgroups):
    mapping.removeGroupFromVirtualGroup(group, virtual_group)
    groups_removed.append((group, virtual_group))

return view.tab_access_groups(
    message_type='feedback', 
    message='Removed groups from virtual groups: %s' % view.quotify_list_ext(groups_removed))
