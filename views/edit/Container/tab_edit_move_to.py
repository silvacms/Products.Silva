## Script (Python) "tab_edit_move_to"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None,new_position=None
##title=
##
model = context.REQUEST.model
view = context

if ids is None or new_position is None:
    return view.tab_edit(
        message_type="error", 
        message="Nothing was selected, so nothing was moved.",
        position=new_position)

if new_position.lower() == 'position':
    return view.tab_edit(
        message_type="error", 
        message="First choose a position number.",
        ids=ids)

actives = []
inactives = []
for id in ids:
    item = model[id]
    if (item.implements_publishable() and item.is_active()
    and not (item.implements_content() and item.is_default())):
        actives.append(item.id)
    else:
        inactives.append(item.id)

result = model.move_to(actives, int(new_position)-1)
if result:
    message = 'Object(s) %s moved' % view.quotify_list(actives)
    if inactives:
        message += ', <span class="error">but could not move %s</span>' % view.quotify_list(inactives)
    return view.tab_edit(message_type="feedback", message=message)
else:
    return view.tab_edit(
        message_type="error", 
        message="Could not move %s." % view.quotify_list(ids))
