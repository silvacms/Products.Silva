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
    return model.get_ordered_publishables()
return model.objectValues(filter)


