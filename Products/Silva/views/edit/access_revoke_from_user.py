## Script (Python) "access_revoke_from_user"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _
request = context.REQUEST
model = context.REQUEST.model

revoke_roles = request.form.get('revoke_roles', None)
if revoke_roles is None:
    return context.tab_access(
        message_type="error",
        message=_("No roles to revoke selected."))

def extract_users_and_roles(in_list):
    out_list = []
    for item in in_list:
        user,role = item.split('||')
        out_list.append((user,role))
    return out_list

#revoked = []
for user, role in extract_users_and_roles(revoke_roles):
    model.sec_revoke(user, [role])
    #revoked.append((user, role))

return context.tab_access(
    message_type="feedback",
    message=_("Role(s) revoked"))
