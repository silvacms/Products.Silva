## Script (Python) "tab_edit_deactivate"
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
    return view.tab_edit(message_type="feedback", message="Nothing was selected, so nothing is deactivated.")

deactivated = []
not_deactivated = []
message_type = 'feedback'
for id in ids:
    item = model[id]
    if (item.implements_publishable() and item.can_deactivate()):
        item.deactivate()
        deactivated.append(item.id)
    else:
        not_deactivated.append(item.id)

if deactivated:
   if not_deactivated:
      message = 'Content %s deactivated, <span class="error">but could not deactivate %s.</span>' % (
          view.quotify_list(deactivated), view.quotify_list(not_deactivated))
   else:
      message = 'Content %s deactivated.' % view.quotify_list(deactivated)
else:
   message = 'Could not deactivate %s.' % view.quotify_list(not_deactivated)
   message_type = 'error'
   
return view.tab_edit(message_type=message_type, message=message)
