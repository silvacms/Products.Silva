## Script (Python) "save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.get_root().security_trigger()
context.save_helper()
context.invalidate_cache_helper()
return context.redirect()
