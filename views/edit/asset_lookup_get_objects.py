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
if filter == 'Asset':
    return model.get_assets()
if filter == 'Content':
    return [ content
        for content in model.get_ordered_publishables()
        if content.implements_content()]
if filter == 'Container':
    return [ content
        for content in model.get_ordered_publishables()
        if content.implements_container()]
if filter == 'Publishables':
    return model.get_ordered_publishables()
return model.objectValues(filter)


