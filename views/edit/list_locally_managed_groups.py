## Script (Python) "list_locally_managed_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
model = request.model

gm = model#.sec_get_groupsmapping()
if not gm:
    return []

return gm.listLocallyManagedZODBGroups()
