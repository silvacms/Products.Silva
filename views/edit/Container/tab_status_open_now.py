##parameters=refs=None
from Products.Silva.i18n import translate as _
view = context
request = view.REQUEST
model = request.model

if not refs:
  return view.tab_status(message_type='error', 
          message=_('Nothing was selected, so nothing was approved.'))

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error', 
        message=view.render_form_errors(e),
        refs=refs)

clear_expiration = result['clear_expiration']

objects = [model.resolve_ref(ref) for ref in refs]
message = context.open_now(objects, clear_expiration)
return view.tab_status(message_type='feedback', message=message)
