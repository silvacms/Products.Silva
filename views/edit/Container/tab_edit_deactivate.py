## Script (Python) "tab_edit_deactivate"
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
    return view.tab_edit(message_type="feedback", message=_("Nothing was selected, so nothing is deactivated."))

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
      message = _('Content ${deactivated} deactivated, <span class="error">but could not deactivate ${not_deactivated}.</span>')
      message.set_mapping({
          'deactivated': view.quotify_list(deactivated),
          'not_deactivated': view.quotify_list(not_deactivated)
          })
   else:
      message = _('Content ${deactivated} deactivated.')
      message.set_mapping({'deactivated': view.quotify_list(deactivated)})
else:
   message = _('Could not deactivate ${not_deactivated}.')
   message.set_mapping({'not_deactivated': view.quotify_list(not_deactivated)})
   message_type = 'error'
   
return view.tab_edit(message_type=message_type, message=message)
