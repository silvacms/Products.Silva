## Script (Python) "clear_mapping"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
map = model.sec_get_groupsmapping()

if map:
    map.clear()

model.sec_cleanup_groupsmapping()

return "map cleared"
