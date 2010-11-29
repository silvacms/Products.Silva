## Script (Python) "tab_status_revoke"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model

if not model.is_approved():
    return context.tab_status(message_type="error", message=_("This content is not approved."))

model.unapprove_version()

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()

return context.tab_status(message_type="feedback", message=_("Revoked approval."))
