##parameters=refs=None

# XXX we should really find some patterns for reuse... almost a 1:1 copy of
# views/edit/Container/tab_status_request_approval.py

from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(
        message_type='error', 
        message=_('Nothing was selected, so no approval was requested.'))

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type="error", 
        message=view.render_form_errors(e),
        refs=refs)

expiration_datetime = result['expiration_datetime']
clear_expiration_flag = result['clear_expiration']

#if not publish_now_flag and not publish_datetime:
#    return view.tab_status(
#        message_type="error", 
#        message=_("First set a publish time"))
 
now = DateTime()

msg = []
approved_ids = []
not_approved = []
not_approved_refs = []
no_date_refs = []

get_name = context.tab_status_get_name

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_approved.append((get_name(obj), _('not a versionable object')))
        not_approved_refs.append(ref)
        continue
    if not obj.get_unapproved_version():
        not_approved.append((get_name(obj), _('no unapproved version')))
        not_approved_refs.append(ref)
        continue
    if obj.is_version_approval_requested():
        not_approved.append((get_name(obj),_('approval already requested')))
        not_approved_refs.append(ref)
        continue
    # publish
    obj.set_unapproved_version_publication_datetime(now)
    # expire
    if clear_expiration_flag:
        obj.set_unapproved_version_expiration_datetime(None)
    elif expiration_datetime:
        obj.set_unapproved_version_expiration_datetime(expiration_datetime)


    message = ('Request for approval via a bulk request in the publish '
                'screen of /%s (automatically generated message)'
                ) % model.absolute_url(1)
    obj.request_version_approval(message)    
    approved_ids.append(get_name(obj))

if approved_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Request approval for: ${ids}')
    message.set_mapping({'ids': view.quotify_list(approved_ids)})
    msg.append(unicode(message))

if not_approved:
    message = _('<span class="error">No request for approval on: ${ids}</span>')
    message.set_mapping({'ids': view.quotify_list_ext(not_approved)})
    msg.append(unicode(message))

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()
    
return view.tab_status(message_type='feedback', message=('<br />'.join(msg)), refs=no_date_refs)
