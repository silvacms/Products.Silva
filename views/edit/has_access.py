## Script (Python) "has_access"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return context.get_silva_permissions()['ChangeSilvaAccess']
