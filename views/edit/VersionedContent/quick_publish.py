## Script (Python) "tab_edit_make_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

return_to = request.get('return_to', 'tab_edit')
view = model.edit[return_to]

if not model.get_unapproved_version():
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # See also edit/Container/tab_status_approve.py
    if model.is_version_published():
        return view(
            message_type="error", 
            message=_("There is no unapproved version to approve."))
    model.create_copy()

import DateTime

model.set_unapproved_version_publication_datetime(DateTime.DateTime())

model.approve_version()

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()


return view(message_type="feedback", message=_("Version approved."))
