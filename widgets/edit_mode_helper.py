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
context.service_editor.setNodeWidget(node,
  context.get_widget_path()[:-1] + ('mode_edit',))
