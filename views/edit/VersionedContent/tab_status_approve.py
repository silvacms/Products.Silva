## Script (Python) "tab_status_approve"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Approve unapproved content
##
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

if model.get_unapproved_version() is None:
    return view.tab_status(message_type="error", message="There is no unapproved version to approve.")

if not model.can_approve():
    # XXX other reasons why this may fail?
    return view.tab_status(message_type="error", message="You cannot approve this content; it is closed.")

try:
    result = view.tab_status_form_editor.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(message_type="error", message=view.render_form_errors(e))

import DateTime

if result['publish_now_flag']:
    model.set_unapproved_version_publication_datetime(DateTime.DateTime())
else:
    model.set_unapproved_version_publication_datetime(result['publish_datetime'])

if result['expires_flag']:
    model.set_unapproved_version_expiration_datetime(result['expiration_datetime'])
else:
    model.set_unapproved_version_expiration_datetime(None)

model.approve_version()

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()
    
return view.tab_status(message_type="feedback", message="Version approved.")
