## Script (Python) "tab_edit_update_index"
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
model.update_index()
return view.tab_edit(message_type='feedback', message="Index updated")
