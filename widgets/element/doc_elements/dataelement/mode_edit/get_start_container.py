## Script (Python) "get_start_container"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Lookup the container to start listing assets
##

ds = context.get_datasource()
if ds is None:
    return context.REQUEST.node.get_container()
else:
    return ds.get_container()