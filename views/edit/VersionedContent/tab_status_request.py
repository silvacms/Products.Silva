from Products.Formulator.Errors import FormValidationError

model = context.REQUEST.model
view = context

try:
    result = view.tab_status_form_author.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(
        message_type="error", message=view.render_form_errors(e))

# check for status
message=None
if model.get_unapproved_version() is None:
    message='There is no unapproved version.'
elif model.is_version_approval_requested():
    message='Approval has already been requested.'
# no check for closed ...

if message is not None:
    return view.tab_status(message_type="error", message=message)

context.set_unapproved_version_publication_datetime(result['publish_datetime'])

expiration = result['expiration_datetime']
if expiration:
    model.set_unapproved_version_expiration_datetime(expiration)
else:
    model.set_unapproved_version_expiration_datetime(None)

model.request_version_approval(result['message'])

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()
    
return view.tab_status(message_type="feedback", message="Approval requested.")
