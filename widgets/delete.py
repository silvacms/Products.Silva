## Script (Python) "delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
node.get_content().sec_update_last_author_info()

context.service_editor.clearNodeWidget(node)
context.invalidate_cache_helper()

node.parentNode.removeChild(node)
return context.redirect()
