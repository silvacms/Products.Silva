## Script (Python) "get_members"
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

def member_cmp(member1, member2):
    return cmp(member1.fullname(), member2.fullname())

local_members = userids_to_members(model.sec_get_local_defined_userids())
upward_members = userids_to_members(model.sec_get_upward_defined_userids())

members_dict = {}
members_dict.update(local_members)
members_dict.update(upward_members)

members = members_dict.values()
members.sort(member_cmp)

return members
