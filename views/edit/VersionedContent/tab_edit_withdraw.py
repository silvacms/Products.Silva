## Script (Python) "tab_status_withdraw"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Withdraw a request for approval on unapproved content
##
# XXX copy from tab_status_withdraw, this version just redirects rather than
# returning the tab
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

is_rejection = request['rejection_status'] == 'true'
if is_rejection:
    message = ("Approval was rejected via the edit screen "
                "(automatically generated message).")
else:
    message = ("Approval was withdrawn via the edit screen. "
                "(automatically generated message)""")


if model.get_unapproved_version() is None:
    if model.get_public_version() is not None:
        if context.get_silva_permissions()['ApproveSilvaContent']:
            return view(message_type="error",
                        message=_("This content is already public. You can "
                                    "close the current public version."))
        else:
            return view(message_type="error",
                        message=_("This content is already public."))
    else:
        return view(message_type="error",
                        message=_("This content is already approved. "
                                    "You can revoke the approval."))

if not model.is_version_approval_requested():
    return view(message_type="error",
                    message=_("No request for approval is pending for "
                                "this content."))

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

request.RESPONSE.redirect('%s/edit?message_type=feedback&message=%s' % (
                                model.absolute_url(), message))
return ''
