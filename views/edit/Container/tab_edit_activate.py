## Script (Python) "tab_edit_activate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context
if ids is None:
    return view.tab_edit(message_type="error", message=_("Nothing was selected, so nothing is activated."))

activated = []
not_activated = []
message_type = 'feedback'
for id in ids:
    item = model[id]
    if (item.implements_publishable() and item.can_activate()):
        item.activate()
        activated.append(item.id)
    else:
        not_activated.append(item.id)

if activated:
   if not_activated:
      message = _('Content ${activated} activated, <span class="error">but could not activate ${not_activated}.</span>')
      message.set_mapping({
          'activated': view.quotify_list(activated),
          'not_activated': view.quotify_list(not_activated)
          })
   else:
      message = _('Content ${activated} activated.')
      message.set_mapping({'activated': view.quotify_list(activated)})
else:
   message = _('Could not activate ${not_activated}.')
   message.set_mapping({'not_activated': view.quotify_list(not_activated)})
   message_type = 'error'

return view.tab_edit(message_type=message_type, message=message)
