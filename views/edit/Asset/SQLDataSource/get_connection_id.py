## Script (Python) "get_connection_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

model = context.REQUEST.model
return model.connection_id()