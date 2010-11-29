##parameters=objects,clear_expiration=False
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model

from DateTime import DateTime
now = DateTime()

approved_ids = []
not_approved = []
msg = []

def action(obj, fullPath, argv):
    if obj.is_version_approved():
        return (False, (fullPath, _('version already approved')))
    if not obj.get_unapproved_version():
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # To revert this behaviour, *uncomment* the next two lines, and *comment*
    # the consecutive four lines.

    #    not_approved.append((get_name(obj), _('no unapproved version available')))
    #    continue
        if obj.is_version_published():
            return (False, (fullPath, _('version already published')))
        obj.create_copy()
    if clear_expiration:
        obj.set_unapproved_version_expiration_datetime(None)
    # publish
    obj.set_unapproved_version_publication_datetime(now)
    obj.approve_version()
    return (True, fullPath)

[approved_ids,not_approved,dummy] = context.do_publishing_action(objects,action=action)

if approved_ids:
    message = _('Approval on: ${ids}',
                mapping={'ids': context.quotify_list(approved_ids)})
    msg.append(translate(message))

if not_approved:    
    message = _('could not approve: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_approved)})
    msg.append("<span class='error'>" + translate(message) + "</span>")

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()

return ', '.join(msg)
