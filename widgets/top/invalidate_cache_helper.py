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
parent = node.parentNode

modes = ['mode_normal', 'mode_insert', 'mode_done', 'mode_edit', 'mode_view']

context.service_editor.invalidateCaches(node, modes)
context.service_editor.invalidateChildCaches(node, modes)

if parent.nodeType == node.ELEMENT_NODE:
    context.service_editor.invalidateCaches(parent, modes)
