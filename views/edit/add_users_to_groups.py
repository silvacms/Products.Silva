## Script (Python) "add_users_to_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=users=None, groups=None
##title=
##
request = context.REQUEST
model = request.model
view = context

if not users or not groups:
    return view.tab_access_groups(message_type="error", message="No users and/or groups selected.")

mapping = model#.sec_get_or_create_groupsmapping()
users_added = []
for user in users:
    for group in groups:
        mapping.addUserToZODBGroup(user, group)
        users_added.append((user, group))

return view.tab_access_groups(
    message_type='feedback',
    message='Users added to groups: %s' % view.quotify_list_ext(users_added))
