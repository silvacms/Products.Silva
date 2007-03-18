## Script (Python) "preview_open_now.py"
##parameters=ids=None
from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model
view = context

from DateTime import DateTime
now = DateTime()

obj = model
message = _('Document published')
message_type = 'feedback'
publish = True
if not obj.implements_versioning():
    message = _('not a versionable object')
    message_type = 'error'
    publish = False
elif obj.is_version_approved():
    message = _('Version already approved')
    message_type = 'error'
    publish = False
if not obj.get_unapproved_version() and not obj.is_version_approved():
    if obj.is_version_published():
        message = _('Document already published')
        message_type = 'error'
        publish = False

if publish:
    # publish
    obj.set_unapproved_version_publication_datetime(now)
    obj.approve_version()

    if hasattr(context, 'service_messages'):
        context.service_messages.send_pending_messages()

request.form['message_type'] = message_type
request.form['message'] = translate(message)
return model.preview_html()
