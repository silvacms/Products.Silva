## Script (Python) "tab_edit_move_down"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id
##title=
##
model = context.REQUEST.model
view = context
result = model.move_object_down(id)
if result:
    return view.tab_edit(message_type="feedback", message="Moved %s down." % view.quotify(id))
else:
    return view.tab_edit(message_type="error", message="Could not move %s down." % view.quotify(id))
