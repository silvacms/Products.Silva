##parameters=refs=None

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime
from Products.Formulator.Errors import FormValidationError

# Check whether there's any checkboxes checked at all...
if not refs:
    return view.tab_status(
        message_type='error', 
        message='Nothing was selected, so no settings were changed.')

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error', 
        message=view.render_form_errors(e))

publish_datetime = result['publish_datetime']
publish_now_flag = result['publish_now_flag']
expiration_datetime = result['expiration_datetime']
clear_expiration_flag = result['clear_expiration']

if not publish_datetime and not expiration_datetime \
        and not clear_expiration_flag and not publish_now_flag:
    return view.tab_status(
        message_type='error', 
        message='No publication nor expiration time nor any of the flags were set.')

now = DateTime()

changed_ids = []
not_changed = []
msg = []

get_name = context.tab_status_get_name
silva_permissions = view.get_silva_permissions()

for ref in refs:
    obj = model.resolve_ref(ref)
    if obj is None:
        continue
    if not obj.implements_versioning():
        not_changed.append((get_name(obj), 'not a versionable object'))
        continue
    # HUGE check to see what actually may or can be changed...
    if silva_permissions['ApproveSilvaContent']:        
        if not obj.get_next_version():
            # No next version, so start looking for the published version
            # since we can change the expiration time for published content.
            if not obj.get_public_version():
                not_changed.append(
                    (get_name(obj), 'no next or public version available'))
                continue
            # cannot publish, so report that when publ. times have been set
            if publish_now_flag or publish_datetime:
                not_changed.append((get_name(obj), 'cannot change publication time of already public versions.'))
            # expire
            if clear_expiration_flag:
                obj.set_public_version_expiration_datetime(None)
            elif expiration_datetime:
                obj.set_public_version_expiration_datetime(expiration_datetime)
        else:
            # expire
            # XXX- aaargll.. I had to put this before the publish code since
            # after setting the publication datetime, the 'next' version
            # might get published and no next version is available anymore...
            if clear_expiration_flag:
                obj.set_next_version_expiration_datetime(None)
            elif expiration_datetime:
                obj.set_next_version_expiration_datetime(expiration_datetime)
            # publish
            if publish_now_flag:
                obj.set_next_version_publication_datetime(now)
            elif publish_datetime:
                obj.set_next_version_publication_datetime(publish_datetime)
        changed_ids.append(get_name(obj))
    else:
        if not obj.get_unapproved_version():
            not_changed.append((get_name(obj), 'no unapproved version'))
            continue
        # publish
        if publish_now_flag:
            obj.set_unapproved_version_publication_datetime(now)
        elif publish_datetime:
            obj.set_unapproved_version_publication_datetime(publish_datetime)
        # expire
        if clear_expiration_flag:
            obj.set_unapproved_version_expiration_datetime(None)
        elif expiration_datetime:
            obj.set_unapproved_version_expiration_datetime(expiration_datetime)
        changed_ids.append(get_name(obj))

if changed_ids:
    request.set('refs', []) # explicit clear since it has value from the form
    request.set('redisplay_timing_form', 0)
    msg.append( 'Changed settings on: %s' % view.quotify_list(changed_ids) )

if not_changed:
    msg.append( '<span class="error">could not change settings on: %s</span>' % view.quotify_list_ext(not_changed) )

return view.tab_status(message_type='feedback', message=(', '.join(msg)) )
