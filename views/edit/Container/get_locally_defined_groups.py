model = context.REQUEST.model
objects = model.objectItems()
groups = []

for id, object in objects:
    try:
        if object.meta_type in ['Silva Group', 'Silva Virtual Group',]:
            groups.append(object)
    except AttributeError, ae:
        pass

groups = [group for group in groups if group.isValid()]
return groups