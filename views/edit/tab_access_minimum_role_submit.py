from Products.Silva.i18n import translate as _
from Products.Silva.adapters.security import getViewerSecurityAdapter

view = context
request = view.REQUEST
model = request.model

viewer_security = getViewerSecurityAdapter(model)

old_role = viewer_security.getMinimumRole()
role = request['role']

# we don't want to change the role if we already set it
if old_role == role and not viewer_security.isAcquired():
    return model.edit['tab_access'](
        message_type='feedback',
        message=_("Minimum role to access has not changed"))

viewer_security.setMinimumRole(role)

msg = _("Minimum role to access is now set to ${role}")
msg.set_mapping({'role': role})
return model.edit['tab_access'](
    message_type='feedback',
    message= msg)
