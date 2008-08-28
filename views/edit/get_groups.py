## Script (Python) "get_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model

groups = model.sec_get_local_defined_groups()
groups.extend(model.sec_get_upward_defined_groups())
groups.sort()

return groups
