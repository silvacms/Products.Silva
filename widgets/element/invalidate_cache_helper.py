## Script (Python) "invalidate_cache_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
context.service_editor.invalidateCaches(
  node, ['mode_normal', 'mode_insert', 'mode_done', 'mode_edit', 'mode_view'])

#context.service_editor.invalidateCaches(
#  node.parentNode, ['mode_normal', 'mode_insert', 'mode_done', 'mode_edit', 'mode_view'])
