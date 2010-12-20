model = context.REQUEST.model
groups = model.objectValues(['Silva Group', 'Silva Virtual Group',
    'Silva IP Group'])
return [group for group in groups if group.isValid()]
