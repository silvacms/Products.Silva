## Script (Python) "tab_status_withdraw"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Withdraw a request for approval on unapproved content
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

is_rejection = request['rejection_status'] == 'true'

# XXX fishy: if no message, we are called from the edit tab ...
# also use dummy message, if author leaves input box empty
message = request.get('message','')
if message:
    message = unicode(message, 'UTF-8')
    view  = context.tab_status
else:
    tab_name = request['tab_name']
    if is_rejection:
        message = _("""Approval was rejected via the ${tab_name} screen
            (automatically generated message).""") 
    else:
        message = _("""Approval was withdrawn via the ${tab_name} screen.
            (automatically generated message)""") 
    message.set_mapping({'tab_name': tab_name})
    # next fish
    if tab_name == 'edit':
        view = context.tab_edit
    else:
        view = context.tab_status


if model.get_unapproved_version() is None:
    if model.get_public_version() is not None:
        if view.get_silva_permissions()['ApproveSilvaContent']:
            return view(message_type="error", message=_("This content is already public. You can close the current public version."))
        else:
            return view(message_type="error", message=_("This content is already public."))
    else:
        return view(message_type="error", message=_("This content is already approved. You can revoke the approval."))

if not model.is_version_approval_requested():
    return view(message_type="error", message=_("No request for approval is pending for this content."))


if is_rejection:
    model.reject_version_approval(message)
else:
    model.withdraw_version_approval(message)

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()

if is_rejection:
    message = _('Rejected request for approval')
else:
    message = _('Withdrew request for approval')

return view(message_type="feedback", message=message)
