## Script (Python) "tab_status_request_approval"
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
    return view.tab_status(message_type='error', message='Nothing selected, so no approval requested')

try:
    result = view.tab_status_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(message_type="error", message=view.render_form_errors(e))

publish_now_flag = result['publish_now_flag']
publish_datetime = result['publish_datetime']
expires_flag = result['expires_flag']
expiration_datetime = result['expiration_datetime']

if not publish_now_flag and not publish_datetime:
    return view.tab_status(message_type="error", message="No publication datetime set.")
 
now = DateTime()

msg = []
approved_ids = []
not_approved = []
not_approved_refs = []

get_name = context.tab_status_get_name

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_approved.append((get_name(obj), 'not a versionable object'))
        not_approved_refs.append(ref)
        continue
    if not obj.get_unapproved_version():
        not_approved.append((get_name(obj), 'no unapproved version'))
        not_approved_refs.append(ref)
        continue
    if obj.is_version_approval_requested():
        not_approved.append((get_name(obj),'approval already requested'))
        not_approved_refs.append(ref)
        continue
    if publish_now_flag:
        obj.set_unapproved_version_publication_datetime(now)
    else:
        obj.set_unapproved_version_publication_datetime(publish_datetime)
    if expires_flag:
        obj.set_unapproved_version_expiration_datetime(expiration_datetime)

    obj.set_approval_request_message('''
Request for approval via bulk request in the publish tab of /%s
(Automatically generated message)''' % model.absolute_url(1))
    obj.request_version_approval()    
    approved_ids.append(get_name(obj))


context.REQUEST.set('refs', [])

if approved_ids:
    msg.append('Request approval for: %s' % view.quotify_list(approved_ids))
if not_approved:
    msg.append('<span class="error">No request for approval on: %s</span>' % view.quotify_list_ext(not_approved))


return view.tab_status(message_type='feedback', message=('<br />'.join(msg)) )
