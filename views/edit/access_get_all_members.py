## Script (Python) "access_get_all_userinfos"
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
userids_to_members = model.sec_get_members_for_userids

local_members = userids_to_members(model.sec_get_local_defined_userids())
upward_members = userids_to_members(model.sec_get_upward_defined_userids())

# If the user is defined both local and upward, consider 
# this user to be local
for userid in local_members.keys():
    try:
        del upward_members[userid]
    except KeyError:
        pass

# If the user in the lookup_selection is not already defined
# on a higer level we may use as a "local user, yet without roles"...
for key, value in view.lookup_get_selection().items():
    if not upward_members.has_key(key):
        if not local_members.has_key(key):
            # ...only if this user was not already defined locally
            # (I know, since we're handling dicts, this check is a bit redundant,
            # nonetheless, it makes thing a tad more clearer. I hope).
            local_members[key] = value


def member_cmp(member1, member2):
    return cmp(member1.fullname(), member2.fullname())

local = local_members.values()
local.sort(member_cmp)

upward = upward_members.values()
upward.sort(member_cmp)

return {'local':local, 'upward':upward}
