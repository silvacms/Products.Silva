## Script (Python) "save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.save_helper()
context.invalidate_cache_helper()
return context.redirect()
