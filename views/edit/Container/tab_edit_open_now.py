##parameters=ids=None
from Products.Silva.i18n import translate as _
request = context.REQUEST
model = request.model

if not ids:
  return context.tab_edit(message_type='error',
          message=_('Nothing was selected, so nothing was approved.'))


objects = [getattr(model, id) for id in ids]
message = context.open_now(objects)
return context.tab_edit(message_type='feedback', message=message)
