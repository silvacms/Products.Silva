model = context.REQUEST.model
groups = model.objectValues(['Silva Group', 'Silva Virtual Group'])
return [group for group in groups if group.isValid()]
