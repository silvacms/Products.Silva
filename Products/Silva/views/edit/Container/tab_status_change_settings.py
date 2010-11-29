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
        message=_('Nothing was selected, so no settings were changed.'))

try:
    result = context.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return context.tab_status(
        message_type='error',
        message=context.render_form_errors(e),
        refs=refs)

publish_datetime = result['publish_datetime']
expiration_datetime = result['expiration_datetime']
clear_expiration_flag = result['clear_expiration']
publish_now_flag = result['publish_now_flag']

if not publish_datetime and not expiration_datetime \
        and not clear_expiration_flag and not publish_now_flag:
    return context.tab_status(
        message_type='error',
        message=_('No publication nor expiration time nor any of the flags were set.'),
        refs=refs)

now = DateTime()

changed_ids = []
not_changed = []
msg = []

objects = []
for ref in refs:
    obj = model.resolve_ref(ref)
    if obj:
        objects.append(obj)

def action(obj,fullPath,argv):
    (publish_datetime, publish_now_flag, expiration_datetime, clear_expiration_flag) = argv
    
    silva_permissions = context.get_silva_permissions()
    # HUGE check to see what actually may or can be changed...
    if silva_permissions['ApproveSilvaContent']:
        if not obj.get_next_version():
            # No next version, so start looking for the published version
            # since we can change the expiration time for published content.
            if not obj.get_public_version():
                return (False, (fullPath, _('no next or public version available')))
            # cannot publish, so report that when publ. times have been set
            if publish_now_flag or publish_datetime:
                return (False, (fullPath, _('cannot change publication time of already public versions.')))
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
        return (True, fullPath)
    else:
        if not obj.get_unapproved_version():
            return (False, (fullPath, _('no unapproved version')))
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
        return (True, fullPath)

[changed_ids,not_changed,dummy] = context.do_publishing_action(objects,action=action,argv=[publish_datetime,publish_now_flag,expiration_datetime,clear_expiration_flag])

if changed_ids:
    request.set('redisplay_timing_form', 0)
    message = _('Changed settings on: ${ids}',
                mapping={'ids': context.quotify_list(changed_ids)})
    msg.append(translate(message))

if not_changed:
    message = _('could not change settings on: ${ids}',
                mapping={'ids': context.quotify_list_ext(not_changed)})
    msg.append("<span class='error'>" + translate(message) + "</span>")

return context.tab_status(message_type='feedback', message=(', '.join(msg)) )
