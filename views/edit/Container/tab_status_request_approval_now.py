##parameters=refs=None

# XXX we should really find some patterns for reuse... almost a 1:1 copy of
# views/edit/Container/tab_status_request_approval.py

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
        message=_('Nothing was selected, so no approval was requested.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type="error",
        message=context.render_form_errors(e),
        refs=refs)

#if not publish_now_flag and not publish_datetime:
#    return context.tab_status(
#        message_type="error",
#        message=_("First set a publish time"))

now = DateTime()

msg = []
approved_ids = []
not_approved = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj, fullPath, argv):
    (expiration_datetime, clear_expiration_flag) = argv
    
    if not obj.get_unapproved_version():
        return (False, (fullPath, _('no unapproved version')))
    if obj.is_version_approval_requested():
        return (False, (fullPath, _('approval already requested')))
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
    return (True, fullPath)

[approved_ids,not_approved,dummy] = context.do_publishing_action(objects,action=action,argv=[result['expiration_datetime'],result['clear_expiration']])

if approved_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Request approval for: ${ids}',
                mapping={'ids': context.quotify_list(approved_ids)})
    msg.append(translate(message))

if not_approved:
    message = _('no request for approval on: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_approved)})
    msg.append("<span class='error'>" + translate(message) + "</span>")

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()

return context.tab_status(message_type='feedback', message=(', '.join(msg)))
