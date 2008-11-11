## Script (Python) "access_revoke_from_group"
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

def extract_groups_and_roles(in_list):
    out_list = []
    for item in in_list:
        group,role = item.split('||')
        out_list.append((group,role))
    return out_list

revoked = []
map = model.sec_get_groupsmapping()
if map:
    for group, role in extract_groups_and_roles(revoke_roles):
        group = unicode(group, 'UTF-8')
        map.revokeRolesFromGroup(group, [role])
        revoked.append((group, role))

model.sec_cleanup_groupsmapping()

msg = _("Role(s) revoked for ${list}",
        mapping={'list': context.quotify_list_ext(revoked)})
return context.tab_access(
    message_type="feedback",
    message=msg)
