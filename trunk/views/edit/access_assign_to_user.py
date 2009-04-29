## Script (Python) "access_assign_to_user"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userids=None, assign_role=None
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
if not assign_role or assign_role == 'None':
    return context.tab_access(message_type="error", message=_("No role selected."))

if not userids:
    return context.tab_access(message_type="error", message=_("No user(s) selected."))

model = request.model
assigned = []
failed = []
for userid in userids:
    try:
        model.sec_assign(userid, assign_role)
    except:
        failed.append(userid)
    else:
        assigned.append(userid)

if assigned:
    if failed:
        return context.tab_access(
            message_type="error",
            message=_("Role(s) assigned for ${good_users} but failed to assign for ${bad_users}.",
                      mapping=dict(good_users=context.quotify_list(assigned),
                                   bad_users=context.quotify_list(failed))))
    return context.tab_access(
        message_type="feedback",
        message=_("Role(s) assigned for ${users}.",
                  mapping=dict(users=context.quotify_list(assigned))))

return context.tab_access(
    message_type="error",
    message=_("No role have been assigned for ${users}.",
              mapping=dict(users=context.quotify_list(failed))))
