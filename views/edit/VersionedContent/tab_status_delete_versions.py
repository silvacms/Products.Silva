## Script (Python) "tab_status_delete_versions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
from Products.Silva.adapters.version_management import getVersionManagementAdapter

view = context
request = context.REQUEST
model = request.model
adapter = getVersionManagementAdapter(model)

if not request.has_key('versions'):
    return view.tab_status(message_type="error", message="No versions selected")

message_type = 'feedback'
messages = []
for version in request['versions']:
    try:
        adapter.deleteVersion(version)
    except Exception, e:
        message_type = 'error'
        messages.append('error deleting %s: %s' % (version, e))
    else:
        messages.append('deleted version %s' % version)

return view.tab_status(message_type=message_type, message=', '.join(messages).capitalize())
