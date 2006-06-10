## Script (Python) "tab_edit_close.py"
##parameters=ids=None
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime

# Check whether there's any checkboxes checked at all...
if not ids:
    return view.tab_edit(
        message_type='error', 
        message=_('Nothing was selected, so nothing was closed.'))

closed_ids = []
not_closed = []
msg = []

get_name = context.tab_status_get_name

for id in ids:
    obj = getattr(model.aq_inner, id)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_closed.append((get_name(obj), _('not applicable')))
        continue
    if not obj.is_version_published():
        not_closed.append((get_name(obj), _('is not published')))
        continue
    obj.close_version()
    #obj.deactivate()
    closed_ids.append(get_name(obj))

if closed_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Closed: ${ids}')
    message.set_mapping({'ids': view.quotify_list(closed_ids)})
    msg.append(translate(message))

if not_closed:
    message = _('<span class="error">could not close: ${ids}</span>')
    message.set_mapping({'ids': view.quotify_list_ext(not_closed)})
    msg.append(translate(message))

return view.tab_edit(message_type='feedback', message=(', '.join(msg)) )
