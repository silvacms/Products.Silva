## Script (Python) "tab_edit_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=
##
model = context.REQUEST.model
view = context

if ids is None:
    return view.tab_edit(message_type="error", message="Nothing was selected, so nothing was copied.")

model.action_copy(ids, context.REQUEST)
message = "Placed %s on the clipboard for copying." % view.quotify_list(ids)
return view.tab_edit(message_type="feedback", message=message)
