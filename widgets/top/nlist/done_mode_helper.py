## Script (Python) "done_mode_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
# no more special editor
context.service_editor.clearEditor(node)
# get widget of node
widget = context.service_editor.getWidget(node)
# put it in done mode
widget.done_mode_helper()
