## Script (Python) "list_groups_in_locally_managed_virtual_group"
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

if not virtual_group:
    return view.tab_access_groups(message_type="error", message="No virtual group selected.")

gm = model#.sec_get_groupsmapping()
if not gm:
    return []

return gm.listGroupsInLocallyManagedVirtualGroup(virtual_group)
