##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=filter
##title=
##

#filter: 'Asset', 'Content' or a certain meta_type

model = context.REQUEST.model
assets = []
if filter == 'Asset':
    assets = model.get_assets()
elif filter == 'Content':
    assets = [ content
        for content in model.get_ordered_publishables()
        if content.implements_content()]
elif filter == 'Container':
    assets = [ content
        for content in model.get_ordered_publishables()
        if content.implements_container()]
elif filter == 'Publishables':
    assets = model.get_ordered_publishables()
else:
    assets = model.objectValues(filter)
assets.sort(lambda a,b: cmp(a.id, b.id))
return assets


