from AccessControl import getSecurityManager

model = context.REQUEST.model
security_manager = getSecurityManager()
result = {}
result['ReadSilvaContent'] = security_manager.checkPermission('Read Silva content', model)
result['ChangeSilvaContent'] = security_manager.checkPermission('Change Silva content', model)
result['ApproveSilvaContent'] = security_manager.checkPermission('Approve Silva content', model)
result['ChangeSilvaAccess'] = security_manager.checkPermission('Change Silva access', model)
result['ChangeSilvaViewRegistry'] = security_manager.checkPermission('Change Silva View Registry', model)
return result
