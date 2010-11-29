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
message_type, message = model.action_paste_to_ghost(context.REQUEST)

model.sec_update_last_author_info()
return context.tab_edit(message_type=message_type, message=message)
