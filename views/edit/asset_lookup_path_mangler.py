##bind context=context
##parameters=asset_context, asset
# $Id: asset_lookup_path_mangler.py,v 1.1.4.1 2003/03/17 15:13:54 zagy Exp $

asset_path = asset.getPhysicalPath()
asset_context = asset_context.split('/')

i = 0
absolute = 0
for i in range(0, min(len(asset_path), len(asset_context))):
    if asset_path[i] != asset_context[i]: 
        absolute = 1
        break
#raise ValueError, (asset_path, asset_context, i)
if not absolute:
    asset_path = asset_path[len(asset_context):]

return '/'.join(asset_path)

