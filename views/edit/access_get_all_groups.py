## Script (Python) "access_get_all_groups"
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

local_groups = model.sec_get_local_defined_groups()
upward_groups = [ group for group in model.sec_get_upward_defined_groups()
                  if group not in local_groups ]

# If the group taken from the pulldown menu is not already defined
# on a higer level we may use as a "local group, yet without roles"...
for group in view.group_get_selection().keys():
    if not group in upward_groups:
        if not group in local_groups:
            # ...only if this group was not already defined locally.
            local_groups.append(group)

local_groups.sort()
upward_groups.sort()

return {'local':local_groups, 'upward':upward_groups}
