##parameters=refs=None
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError
from zope.i18n import translate

# Check whether there's any checkboxes checked at all...
if not refs:
    return context.tab_status(
        message_type='error',
        message=_('Nothing was selected, so no approval was revoked.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type='error',
        message=context.render_form_errors(e),
        refs=refs)

revoked_ids = []
not_revoked = []
msg = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj, fullPath, argv):
    if not obj.is_version_approved():
        return (False, (fullPath, _('it\'s not approved, or it\'s already published')))
    obj.unapprove_version()
    return (True, fullPath)

[revoked_ids,not_revoked, dummy] = context.do_publishing_action(objects,action=action)

if revoked_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Revoked approval of: ${ids}',
                mapping={'ids': context.quotify_list(revoked_ids)})
    msg.append(translate(message))

if not_revoked:
    message = _('could not revoke approval of: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_revoked)})
    msg.append('<span class="error">' + translate(message) + '</span>')

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()

return context.tab_status(message_type='feedback', message=(', '.join(msg)) )
