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
    userinfo = model.sec_get_user_info(userid)
    if userinfo is None:
        continue
    selection[userid] = userinfo

return view.tab_access_lookup(
    message_type="feedback", 
    message="Selected users.")
