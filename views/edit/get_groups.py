## Script (Python) "get_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
model = context.REQUEST.model

groups = {}
for group in model.sec_get_local_defined_groups():
    groups[group] = group
for group in model.sec_get_upward_defined_groups():
    groups[group] = group

groups = groups.keys()
groups.sort()

return groups
