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
context.REQUEST.node.get_content().sec_update_last_author_info()
context.invalidate_cache_helper()
return context.redirect()
