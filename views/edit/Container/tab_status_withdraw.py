##parameters=refs=None

request = context.REQUEST
model = request.model
view = context

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(
        message_type='error',
        message='Nothing was selected, so no approval was withdrawn.')

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
        continue
    if not obj.get_unapproved_version():
        not_approved.append((get_name(obj),'no unapproved version'))
        continue
    if not obj.is_version_approval_requested():
        not_approved.append((get_name(obj),'no approval requested'))
        not_approved_refs.append(ref)
        continue
    message = '''\
Request for approval was withdrawn via a bulk operation in the publish screen of /%s
(automatically generated message)''' % model.absolute_url(1)
    obj.withdraw_version_approval(message)
    approved_ids.append(obj.id)

if approved_ids:
    request.set('redisplay_timing_form', 0)
    msg.append( 'Withdrawn request for approval for: %s' % view.quotify_list(approved_ids))

if not_approved:
    msg.append( '<span class="error">Not withdrawn: %s</span>' % view.quotify_list_ext(not_approved))

if hasattr(context, 'service_messages'):
    context.service_messages.send_pending_messages()
    
return view.tab_status(message_type='feedback', message=('<br />'.join(msg)) )
