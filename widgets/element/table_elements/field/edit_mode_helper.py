## Script (Python) "edit_mode_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
context.invalidate_cache_helper()
context.service_editor.pushRoot(node, 'service_sub_editor')
