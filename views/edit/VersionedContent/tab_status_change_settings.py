## Script (Python) "tab_status_change_settings"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

if model.get_approved_version() is None:
    return view.tab_status(message_type="error", message="There is no approved version.")

try:
    result = view.tab_status_form_change_settings.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(message_type="error", message=view.render_form_errors(e))

import DateTime

if result['publish_now_flag']:
    model.set_approved_version_publication_datetime(DateTime.DateTime())
else:
    model.set_approved_version_publication_datetime(result['publish_datetime'])

if result['expires_flag']:
    model.set_approved_version_expiration_datetime(result['expiration_datetime'])
else:
    model.set_approved_version_expiration_datetime(None)

return view.tab_status(message_type="feedback", message="Changed publication settings.")
