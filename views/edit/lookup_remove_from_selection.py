## Script (Python) "lookup_remove_from_selection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ruserids=None
##title=
##
model = context.REQUEST.model
view = context

if ruserids is None:
    return view.tab_access_lookup(message_type="error", message="No users removed.")

selection = view.lookup_get_selection()
for userid in ruserids:
    if selection.has_key(userid): 
        del selection[userid]

return view.tab_access_lookup(
    message_type="feedback", 
    message="Removed users from selection.")
