## Script (Python) "add_locally_managed_virtual_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=virtual_group=None
##title=
##
request = context.REQUEST
model = request.model
view = context

if not virtual_group:
    return view.tab_access_groups(message_type="error", message="No group name given")

mapping = model#.sec_get_or_create_groupsmapping()
group_service = context.service_groups
if group_service.groupExists(virtual_group):
    return view.tab_access_groups(
        message_type="error", 
        message="This Silva site already has a (virtual) group defined by this name (%s). Please choose another name" % view.quotify(virtual_group))

mapping.addVirtualGroup(virtual_group)
return view.tab_access_groups(
    message_type='feedback', 
    message="Virtual group %s added." % view.quotify(virtual_group))
