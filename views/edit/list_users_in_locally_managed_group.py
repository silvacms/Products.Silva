## Script (Python) "list_users_in_locally_managed_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=group=None
##title=
##
request = context.REQUEST
model = request.model

if not group:
    return view.tab_access_groups(message_type="error", message="No group selected.")

gm = model#.sec_get_groupsmapping()
if not gm:
    return []

return gm.listUsersInLocallyManagedGroup(group)
