## Script (Python) "register_all"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.clear()
context.register_silva_core()
context.register_silva_eur()
context.register_silva_ing()

return "Done"
