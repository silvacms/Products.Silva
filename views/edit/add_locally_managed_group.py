## Script (Python) "add_locally_managed_group"
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
view = context
mapping = model#.sec_get_or_create_groupsmapping()

if not group:
    return view.tab_access_groups(message_type="error", message="No group name given.")

group_service = context.service_groups
if group_service.groupExists(group):
    return view.tab_access_groups(
        message_type="error", 
        message="This Silva site already has a group defined by this name (%s). Please choose another name" % view.quotify(group))

mapping.addZODBGroup(group)

return view.tab_access_groups(
    message_type='feedback', 
    message="Group %s added." % view.quotify(group))
