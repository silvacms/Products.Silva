## Script (Python) "access_remove_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groups=None
##title=
##
view = context
model = context.REQUEST.model
map = model.sec_get_groupsmapping()

if not groups:
    return view.tab_access(
        message_type="error", message="No groups(s) selected, so none removed")

removed = []
if map:
    mapped_groups = map.getMappings().keys()
    for group in groups: 
        if group in mapped_groups:
            map.removeMapping(group)
            removed.append((group))

model.sec_cleanup_groupsmapping()
view.group_remove_from_selection(groups)

return view.tab_access(
    message_type="feedback", 
    message="Removed group(s) %s" % view.quotify_list(removed))
