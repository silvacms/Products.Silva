## Script (Python) "remove_users_from_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=users_groups=None
##title=
##
request = context.REQUEST
model = request.model
view = context

if not users_groups:
    return view.tab_access_groups(message_type="error", message="No users selected.")

def extract_users_groups(in_list):
    out_list = []
    for item in in_list:
        user, group = item.split('||')
        out_list.append((user, group))
    return out_list

mapping = model#.sec_get_groupsmapping()
users_removed = []
for user, group in extract_users_groups(users_groups):
    mapping.removeUserFromZODBGroup(user, group)
    users_removed.append((user, group))

return view.tab_access_groups(
    message_type='feedback',
    message='Users removed from groups: %s' % view.quotify_list_ext(users_removed))
