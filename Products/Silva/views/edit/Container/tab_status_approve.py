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
        message=_('Nothing was selected, so nothing was approved.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type='error',
        message=context.render_form_errors(e),
        refs=refs)

#if not publish_now_flag and not publish_datetime:
#    return context.tab_status(
#        message_type='error',
#        message='No publication datetime set.')

now = DateTime()

approved_ids = []
not_approved = []
no_date_refs = []
msg = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj,fullPath,argv):
    (publish_datetime, publish_now_flag, expiration_datetime, clear_expiration_flag) = argv
    
    if obj.is_version_approved():
        return (False, (fullPath, _('version already approved')))
    if ((publish_now_flag or publish_datetime) and
            not obj.get_unapproved_version()):
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # To revert this behaviour, *uncomment* the next two lines, and *comment*
    # the consecutive four lines.

    #    not_approved.append((get_name(obj), _('no unapproved version available')))
    #    continue
        if obj.is_version_published():
            return (False, (fullPath, _('version already public')))
        obj.create_copy()
    # publish
    if publish_now_flag:
        obj.set_unapproved_version_publication_datetime(now)
    elif publish_datetime:
        obj.set_unapproved_version_publication_datetime(publish_datetime)
    elif not obj.get_unapproved_version_publication_datetime():
        # no date set, neither on unapproved version nor in tab_status form
        return (False, (fullPath, _('no publication time was set'), context.create_ref(obj)))
    # expire
    if clear_expiration_flag:
        obj.set_unapproved_version_expiration_datetime(None)
    elif expiration_datetime:
        obj.set_unapproved_version_expiration_datetime(expiration_datetime)

    obj.approve_version()
    return (True, fullPath)

[approved_ids,not_approved,no_date_refs] = context.do_publishing_action(objects,action=action,argv=[result['publish_datetime'],result['publish_now_flag'],result['expiration_datetime'],result['clear_expiration']])

if approved_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Approval on: ${ids}',
                mapping={'ids': context.quotify_list(approved_ids)})
    msg.append(translate(message))

if not_approved:    
    message = _('could not approve: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_approved)})
    msg.append("<span class='error'>" + translate(message) + "</span>")

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()

return context.tab_status(message_type='feedback', message=(', '.join(msg)), refs=no_date_refs)
