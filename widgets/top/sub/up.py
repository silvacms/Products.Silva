## Script (Python) "up"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.service_editor.popRoot(context.REQUEST.node)
return context.redirect()
