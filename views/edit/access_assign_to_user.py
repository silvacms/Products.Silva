## Script (Python) "access_assign_to_user"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids=None, assign_role=None
##title=
##
view = context
if not assign_role or assign_role == 'None':
    return view.tab_access(message_type="error", message="No role selected.")

if not userids:
    return view.tab_access(message_type="error", message="No user(s) selected.")

model = context.REQUEST.model
#assigned = []
for userid in userids:
    model.sec_assign(userid, assign_role)
    #assigned.append((userid, assign_role))

#return view.tab_access(
#    message_type="feedback", 
#    message="Role(s) assigned") # for %s" % view.quotify_list_ext(assigned))

# FIXME: do we need feedback?
request.RESPONSE.redirect(view.tab_access.absolute_url())