## Script (Python) "remove_locally_managed_virtual_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=virtual_groups=None
##title=
##
request = context.REQUEST
model = request.model
view = context

if not virtual_groups:
    return view.tab_access_groups(message_type="error", message="No virtual group(s) selected.")

mapping = model#.sec_get_groupsmapping()
deleted_virtual_groups = []
non_deleted_virtual_groups = []
for virtual_group in virtual_groups:
    try:
        mapping.removeVirtualGroup(virtual_group)
        deleted_virtual_groups.append(virtual_group)
    except: #GroupsError, err:
        non_deleted_virtual_groups.append(virtual_group)
    
message = ""
if deleted_virtual_groups:
    message += "Virtual group(s) %s removed." % view.quotify_list(deleted_virtual_groups)
if non_deleted_virtual_groups:
    message += " Could not remove: %s" % view.quotify_list(non_deleted_virtual_groups)

return view.tab_access_groups(
    message_type='feedback', message=message)
