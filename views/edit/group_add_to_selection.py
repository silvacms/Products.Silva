## Script (Python) "group_add_to_selection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=add_group
##title=
##
model = context.REQUEST.model
view = context

selection = view.group_get_selection()
selection[add_group] = add_group

return view.tab_access()
