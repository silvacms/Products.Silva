## Script (Python) "save_and_insert"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

request = context.REQUEST
node = request.node
if not node.get_content().sec_create_lock():
    return context.redirect()

node.get_content().sec_update_last_author_info()

context.save_helper()
context.invalidate_cache_helper()

if request.has_key('element_switched'):
    return context.redirect()

context.done_mode()
return context.service_editor.getWidget(node).insert_mode()
