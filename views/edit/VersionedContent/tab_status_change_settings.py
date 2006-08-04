from Products.Silva.i18n import translate as _
from Products.Formulator.Errors import ValidationError, FormValidationError
import DateTime

model = context.REQUEST.model
view = context

if model.get_approved_version() is None:
    return view.tab_status(
        message_type="error", 
        message=_("There is no approved version."))

try:
    result = view.tab_status_form_change_settings.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(
        message_type="error", message=view.render_form_errors(e))

expiration = result['expiration_datetime']
clear_expiration_flag = result['clear_expiration']
if expiration:
    model.set_approved_version_expiration_datetime(expiration)
if clear_expiration_flag:
    model.set_approved_version_expiration_datetime(None)
        
model.set_approved_version_publication_datetime(result['publish_datetime'])

return view.tab_status(
    message_type="feedback", message=_("Changed publication settings."))
