from Products.Silva.adapters.security import getViewerSecurityAdapter
from Products.Silva.roleinfo import ASSIGNABLE_VIEWER_ROLES

model = context.REQUEST.model

viewer_security = getViewerSecurityAdapter(model)

acquired = viewer_security.isAcquired()
selected_role = viewer_security.getMinimumRole()
above_role = viewer_security.getMinimumRoleAbove()
is_public = selected_role == 'Anonymous'

viewer_roles = ASSIGNABLE_VIEWER_ROLES
if not is_public and above_role != 'Anonymous':
    viewer_roles = ASSIGNABLE_VIEWER_ROLES[1:]
    
return {
    'acquired': acquired,
    'selected_role': selected_role,
    'viewer_roles': viewer_roles,
    'is_public': is_public,
    }
