## Script (Python) "tab_edit_move_up"
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
result = model.move_object_up(id)
if result:
    return view.tab_edit(message_type="feedback", message="Moved %s up." % view.quotify(id))
else:
    return view.tab_edit(message_type="error", message="Could not move %s up." % view.quotify(id))
