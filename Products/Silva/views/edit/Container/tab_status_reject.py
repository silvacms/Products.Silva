##parameters=refs=None
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return context.tab_status(
        message_type='error',
        message=_('Nothing was selected, so no approval was rejected.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type="error",
        message=context.render_form_errors(e),
        refs=refs)

msg = []
approved_ids = []
not_approved = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj, fullPath, argv):
    if not obj.get_unapproved_version():
        return (False, (fullPath, _('no unapproved version')))
    if not obj.is_version_approval_requested():
        return (False, (fullPath, _('no approval requested')))
    message = ('Request for approval was rejected via a bulk operation in '
                'the publish screen of /%s (automatically generated message)'
                ) % model.absolute_url(1)
    obj.reject_version_approval(message)
    return (True, fullPath)

[approved_ids,not_approved,dummy] = context.do_publishing_action(objects,action=action)

if approved_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Rejected request for approval for: ${ids}',
                mapping={'ids': context.quotify_list(approved_ids)})
    msg.append(translate(message))

if not_approved:
    message = _('not rejected: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_approved)})
    msg.append('<span class="error">' + translate(message) + '</span>')

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()

return context.tab_status(message_type='feedback', message=(', '.join(msg)) )
