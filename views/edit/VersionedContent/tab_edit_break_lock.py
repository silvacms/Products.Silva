## Script (Python) "tab_edit_break_lock"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
model.sec_break_lock()
return context.tab_edit(message_type="feedback", message="Lock broken")
