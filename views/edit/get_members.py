## Script (Python) "get_members"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
#userids_to_members = model.sec_get_members_for_userids
userid_to_member = model.sec_get_member

def member_cmp(member1, member2):
    return cmp(member1.fullname(), member2.fullname())

local_ids = model.sec_get_local_defined_userids()
upward_ids = model.sec_get_upward_defined_userids()

# Filter out "Unknown Users". Should the corresponding userids 
# be deleted from the local roles?
members_dict = {}
for id in (local_ids + upward_ids):
    member = userid_to_member(id)
    if not member.userid() == 'unknown':
        members_dict[id] = member

members = members_dict.values()
members.sort(member_cmp)

return members
