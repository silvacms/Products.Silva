## Script (Python) "save_and_exit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.get_root().security_trigger()
request = context.REQUEST
node = request.node
context.save_helper()
context.invalidate_cache_helper()
if not request.has_key('element_switched'):
    context.done_mode() 
return context.redirect()
