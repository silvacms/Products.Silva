## Script (Python) "lookup_add_to_selection"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids=None
##title=
##
model = context.REQUEST.model
view = context

if userids is None:
    return view.tab_access_lookup(message_type="error", message="No users selected.")

selection = view.lookup_get_selection()
for userid in userids:
    member = model.sec_get_member(userid)
    if member is None:
        continue
    selection[userid] = member

return view.tab_access_lookup(
    message_type="feedback", 
    message="Selected users.")
