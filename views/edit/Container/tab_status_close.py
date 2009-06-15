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
        message=_('Nothing was selected, so nothing was closed.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type='error',
        message=context.render_form_errors(e),
        refs=refs)

closed_ids = []
not_closed = []
msg = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj,fullPath,argv):
    if not obj.is_version_published():
        return (False, (fullPath, _('is not published')))
    obj.close_version()
    return (True, fullPath)

[closed_ids,not_closed,dummy] = context.do_publishing_action(objects,action=action)

if closed_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Closed: ${ids}',
                mapping={'ids': context.quotify_list(closed_ids)})
    msg.append(translate(message))

if not_closed:
    message = _('could not close: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_closed)})
    msg.append("<span class='error'>" + translate(message) + "</span>")

return context.tab_status(message_type='feedback', message=(', '.join(msg)) )
