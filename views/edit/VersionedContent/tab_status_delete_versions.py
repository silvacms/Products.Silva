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

if len(request['versions']) == len(adapter.getVersionIds()):
    return view.tab_status(message_type="error", message="Can't delete all versions")
    
result = adapter.deleteVersions(request['versions'])

messages = []
for id, error in result:
    if error is not None:
        messages.append('<span class="error">could not delete %s: %s</span>' % (id, error))
    else:
        messages.append('deleted %s' % id)

return view.tab_status(message_type="feedback", message=', '.join(messages).capitalize())
