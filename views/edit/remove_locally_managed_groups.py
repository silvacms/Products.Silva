## Script (Python) "remove_locally_managed_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groups=None
##title=
##
#from Products.Groups.GroupsErrors import GroupsError

request = context.REQUEST
model = request.model
view = context

if not groups:
    return view.tab_access_groups(message_type="error", message="No group(s) seelected")

mapping = model#.sec_get_groupsmapping()

deleted_groups = []
non_deleted_groups = []
for group in groups:
    try:
        mapping.removeZODBGroup(group)
        deleted_groups.append(group)
    except: #GroupsError, err:
        non_deleted_groups.append(group)

message = ""
if deleted_groups:
    message += "Group(s) %s removed." % view.quotify_list(deleted_groups)
if non_deleted_groups:
    message += " Could not remove: %s" % view.quotify_list(non_deleted_groups)

return view.tab_access_groups(
    message_type='feedback', message=message)
