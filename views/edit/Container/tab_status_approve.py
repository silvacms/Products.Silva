## Script (Python) "tab_status_approve"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=refs=None
##title=
##
model = context.REQUEST.model
view = context
from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(message_type='error', message='Nothing was selected, so nothing approved')

try:
    result = view.tab_status_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(message_type='error', message=view.render_form_errors(e))

publish_now_flag = result['publish_now_flag']
publish_datetime = result['publish_datetime']
expires_flag = 1 #result['expires_flag']
expiration_datetime = result['expiration_datetime']

if not publish_now_flag and not publish_datetime:
    return view.tab_status(message_type='error', message='No publication datetime set.')
 
now = DateTime()

approved_ids = []
not_approved = []
msg = []

get_name = context.tab_status_get_name

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_approved.append((get_name(obj), 'not a versionable object'))
        continue
    if obj.is_version_approved():
        not_approved.append((get_name(obj), 'version already approved'))
        continue
    if not obj.can_approve():
        not_approved.append((get_name(obj), 'content object is closed'))
        continue
    if not obj.get_unapproved_version():
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # To revert this behaviour, *uncomment* the next two lines, and *comment*
    # the consecutive four lines.

    #    not_approved.append((get_name(obj), 'no unapproved version available'))
    #    continue
        if obj.is_version_published():
            not_approved.append((get_name(obj), 'version already public'))
            continue
        obj.create_copy()

    if publish_now_flag:
        obj.set_unapproved_version_publication_datetime(now)
    else:
        obj.set_unapproved_version_publication_datetime(publish_datetime)
    if expires_flag:
        obj.set_unapproved_version_expiration_datetime(expiration_datetime)
    obj.approve_version()
    approved_ids.append(get_name(obj))

if approved_ids:
    msg.append( 'Approval on: %s' % view.quotify_list(approved_ids) )

if not_approved:
    msg.append( '<span class="error">could not approve: %s</span>' % view.quotify_list_ext(not_approved) )

context.REQUEST.set('refs', [])

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()
    
return view.tab_status(message_type='feedback', message=(', '.join(msg)) )
