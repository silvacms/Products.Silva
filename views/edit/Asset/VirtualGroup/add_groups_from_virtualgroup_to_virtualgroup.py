##parameters=groups=None

request = context.REQUEST
model = request.model
view = context

groupids = {}

if not groups:
    return view.tab_edit(
        message_type="error", 
        message="No group(s) selected, so nothing to use to add groups.")

def handle_groups(virtualgroups):
    groups_service = getattr(context, 'service_groups')
    for virtualgroup in virtualgroups:        
        if groups_service.isVirtualGroup(virtualgroup):
            for group in groups_service.listGroupsInVirtualGroup(virtualgroup):
                groupids[group] = 1

handle_groups(groups)
return view.add_groups_to_virtualgroup(groups=groupids.keys())