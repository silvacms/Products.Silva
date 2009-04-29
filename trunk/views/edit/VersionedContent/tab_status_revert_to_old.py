## Script (Python) "tab_edit_revert_to_saved"
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
if not request.has_key('versions'):
    return context.tab_status(message_type="error", message=_("No version selected to copy."))

from Products.Silva.adapters import version_management
adapter = version_management.getVersionManagementAdapter(model)

versions = request['versions']
if len(versions) > 1:
    return context.tab_status(message_type="error", message=_("Can only set 1 version as editable."))
version = versions[0]
model.sec_update_last_author_info()
try:
    adapter.revertPreviousToEditable(version)
except Exception, e:
    return context.tab_status(message_type="error", message=e)

return context.tab_status(message_type="feedback", message=_("Reverted to previous version."))
