model = context.REQUEST.model
group_types = ['Silva Group', 'Silva Virtual Group', 'Silva IP Group']
localgroups_ids = [ g.id for g in model.objectValues(group_types) ]
groups = [ g.getObject() for g in context.service_catalog(meta_type = group_types)
           if g.id not in localgroups_ids ]
return groups
