## Script (Python) "get_addables_allowed"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model

return model.get_silva_addables_allowed_in_publication()
