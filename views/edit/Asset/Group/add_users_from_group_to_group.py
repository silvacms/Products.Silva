##parameters=groups=None

request = context.REQUEST
model = request.model
view = context

if not groups:
    return view.tab_access(
        message_type="error", 
        message="No group(s) selected, so nothing to use to add users.")

def handle_groups(groups):
    groups_service = getattr(context, 'service_groups')
    for group in groups:        
        if groups_service.isVirtualGroup(group):
            handle_groups(groups_service.listGroupsInVirtualGroup(group))

        elif groups_service.isNormalGroup(group):
            for userid in groups_service.listUsersInZODBGroup(group):
                userids[userid] = 1

userids = {}
handle_groups(groups)
return view.add_users_to_group(userids=userids.keys())