## Script (Python) "group_remove_from_selection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=remove_groups
##title=
##
model = context.REQUEST.model
view = context

selection = view.group_get_selection()
for remove_group in remove_groups:
    if selection.has_key(remove_group): 
        del selection[remove_group]

return view.tab_access()
