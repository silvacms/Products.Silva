## Script (Python) "get_acquire_addables_checked"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model

return model.is_silva_addables_acquired()
