## Script (Python) "get_user_role"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This script has a "Proxy Role" as "Manager" since I was not sure on
# changing the permission declarations in the Silva Security module for
# "sec_get_roles_for_userid()"
# 
model = context.REQUEST.model
user = context.REQUEST.AUTHENTICATED_USER

return ''.join(model.sec_get_roles_for_userid(user.getId())[-1:])
