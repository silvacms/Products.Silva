## Script (Python) "tab_edit_paste_to_ghost"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
view = context
model.action_paste_to_ghost(context.REQUEST)
return view.tab_edit(message_type="feedback", message="Content pasted to ghost.")
