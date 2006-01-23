##parameters=refs=None
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError
from zope.i18n import translate

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(
        message_type='error', 
        message=_('Nothing was selected, so no approval was revoked.'))

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error', 
        message=view.render_form_errors(e),
        refs=refs)

revoked_ids = []
not_revoked = []
msg = []

get_name = context.tab_status_get_name

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_revoked.append((get_name(obj), _('not a versionable object')))
        continue
    if not obj.is_version_approved():
        not_revoked.append((get_name(obj), _('it\'s not approved, or it\'s already published')))
        continue
    obj.unapprove_version()
    revoked_ids.append(get_name(obj))

if revoked_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Revoked approval of: ${ids}')
    message.set_mapping({'ids': view.quotify_list(revoked_ids)})
    msg.append(translate(message))

if not_revoked:
    message = _('Could not revoke approval of: ${ids}')
    message.set_mapping({'ids': view.quotify_list_ext(not_revoked)})
    msg.append('<span class="error">' + translate(message) + '</span>')

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()
    
return view.tab_status(message_type='feedback', message=(', '.join(msg)) )
