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
userids_to_userinfo = model.sec_get_userinfos_for_userids

local_userinfos = userids_to_userinfo(model.sec_get_local_defined_userids())
upward_userinfos = userids_to_userinfo(model.sec_get_upward_defined_userids())

# If the user is defined both local and upward, consider 
# this user to be local
for userid in local_userinfos.keys():
    try:
        del upward_userinfos[userid]
    except KeyError:
        pass

# If the user in the lookup_selection is not already defined
# on a higer level we may use as a "local user, yet without roles"...
for key, value in view.lookup_get_selection().items():
    if not upward_userinfos.has_key(key):
        if not local_userinfos.has_key(key):
            # ...only if this user was not already defined locally
            # (I know, since we're handling dicts, this check is a bit redundant,
            # nonetheless, it makes thing a tad more clearer. I hope).
            local_userinfos[key] = value


def userinfo_cmp(userinfo1, userinfo2):
    return cmp(userinfo1['cn'], userinfo2['cn'])

local = local_userinfos.values()
local.sort(userinfo_cmp)

upward = upward_userinfos.values()
upward.sort(userinfo_cmp)

return {'local':local, 'upward':upward}
