##parameters=refs=None
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(
        message_type='error',
        message=_('Nothing was selected, so no new version was created.'))

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error',
        message=view.render_form_errors(e),
        refs=refs)

copied_ids = []
not_copied = []
msg = []

get_name = context.tab_status_get_name

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_copied.append((get_name(obj), _('not applicable')))
        continue
    if obj.get_next_version():
        not_copied.append((get_name(obj), _('already has a next version')))
        continue
    obj.create_copy()
    copied_ids.append(get_name(obj))

if copied_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Created a new version for: ${ids}')
    message.set_mapping({'ids': view.quotify_list(copied_ids)})
    msg.append(translate(message))

if not_copied:
    message = _('could not create a new version for: ${ids}')
    message.set_mapping({'ids': view.quotify_list_ext(not_copied)})
    msg.append('<span class="error">' + translate(message)  + '</span>')

return view.tab_status(message_type='feedback', message=(', '.join(msg)) )
