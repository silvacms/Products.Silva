from Products.Silva.adapters.security import getViewerSecurityAdapter

view = context
request = view.REQUEST
model = request.model

viewer_security = getViewerSecurityAdapter(model)

viewer_security.setAcquired()

return model.edit['tab_access'](
    message_type="feedback",
    message="Minimum role to access is now acquired")
