##parameters=refs=None

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(
        message_type='error', 
        message='Nothing was selected, so nothing was closed.')

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error', 
        message=view.render_form_errors(e))

closed_ids = []
not_closed = []
msg = []

get_name = context.tab_status_get_name

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_closed.append((get_name(obj), 'not a versionable object'))
        continue
    if not obj.is_version_published():
        not_closed.append((get_name(obj), 'is not published'))
        continue
    obj.close_version()
    #obj.deactivate()
    closed_ids.append(get_name(obj))

if closed_ids:
    request.set('refs', [])
    request.set('redisplay_timing_form', 0)
    msg.append( 'Closed: %s' % view.quotify_list(closed_ids) )

if not_closed:
    msg.append( '<span class="error">could not close: %s</span>' % view.quotify_list_ext(not_closed) )

return view.tab_status(message_type='feedback', message=(', '.join(msg)) )
