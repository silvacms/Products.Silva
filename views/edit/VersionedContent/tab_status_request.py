## Script (Python) "tab_status_request"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Request approval
##
model = context.REQUEST.model
view = context

result = view.tab_status_form_author.validate_all(context.REQUEST)

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

if result['expires_flag']:
    model.set_unapproved_version_expiration_datetime(
       result['expiration_datetime'])
else:
    model.set_unapproved_version_expiration_datetime(None)

model.set_approval_request_message(result['message'])
model.request_version_approval()

return view.tab_status(message_type="feedback", message="Approval requested.")
