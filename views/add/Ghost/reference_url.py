##parameters=asset_context
return '%s/edit/asset_lookup?filter=Content&asset_context=%s' % (
    asset_context.absolute_url(),
    '/'.join(asset_context.getPhysicalPath()))
