model = context.REQUEST.model
assets = model.get_assets()
groups = []

for asset in assets:
    if asset.meta_type in ['Silva Group', 'Silva Virtual Group',]:
        groups.append(asset)

groups = [group for group in groups if group.isValid()]
return groups