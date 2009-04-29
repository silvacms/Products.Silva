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

get_name = context.tab_status_get_name

for obj in objects:
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_approved.append((get_name(obj), _('not applicable')))
        continue
    if obj.is_version_approved():
        not_approved.append((get_name(obj), _('version already approved')))
        continue
    if not obj.get_unapproved_version():
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # To revert this behaviour, *uncomment* the next two lines, and *comment*
    # the consecutive four lines.

    #    not_approved.append((get_name(obj), _('no unapproved version available')))
    #    continue
        if obj.is_version_published():
            not_approved.append((get_name(obj), _('version already published')))
            continue
        obj.create_copy()
    if clear_expiration:
        obj.set_unapproved_version_expiration_datetime(None)
    # publish
    obj.set_unapproved_version_publication_datetime(now)
    obj.approve_version()
    approved_ids.append(get_name(obj))

if approved_ids:
    message = _('Approval on: ${ids}',
                mapping={'ids': context.quotify_list(approved_ids)})
    msg.append(translate(message))

if not_approved:
    message = _('could not approve: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_approved)})
    msg.append(translate(message))

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()

return ', '.join(msg)
