## Script (Python) "tab_edit_revert_to_saved"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
request = view.REQUEST
model = request.model
if not request.has_key('versions'):
    return view.tab_status(message_type="error", message="No version selected to copy.")

from Products.Silva.adapters import version_management
adapter = version_management.getVersionManagementAdapter(model)

version = request['versions']
if same_type(version, []):
    return view.tab_status(message_type="error", message="Can only set 1 version as editable.")
    
model.sec_update_last_author_info()
try:
    adapter.revertEditableToOld(version)
except Exception, e:
    return view.tab_status(message_type="error", message=e)

return view.tab_status(message_type="feedback", message="Reverted to previous version.")
