# This script has a "Proxy Role" as "Manager" since I was not sure on
# changing the permission declarations in the Silva Security module for
# "sec_get_roles_for_userid()"
# 
model = context.REQUEST.model

if model is None:
    return ''

return '/'.join(model.sec_get_all_roles())
