## Script (Python) "list_all_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
gs = context.service_groups
return gs.listAllGroups()
