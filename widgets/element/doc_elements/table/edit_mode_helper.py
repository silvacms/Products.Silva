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
context.service_editor.setEditor(node, 'service_table_editor')
