## Script (Python) "tab_access_assign"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids, assign_role
##title=
##
view = context
if assign_role == 'None':
    return view.tab_access(message_type="error", message="No role selected.")

if not userids:
    return view.tab_access(message_type="error", message="No users selected.")

model = context.REQUEST.model
assigned = []
for userid in userids:
    model.sec_assign(userid, assign_role)
    assigned.append((userid, assign_role))

return view.tab_access(
    message_type="feedback", 
    message="Local role(s) assigned for %s" % view.quotify_list_ext(assigned))
