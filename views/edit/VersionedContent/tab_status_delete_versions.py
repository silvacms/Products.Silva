## Script (Python) "tab_status_delete_versions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
from Products.Silva.i18n import translate as _
from Products.Silva.adapters.version_management import getVersionManagementAdapter

view = context
request = context.REQUEST
model = request.model
adapter = getVersionManagementAdapter(model)

if not request.has_key('versions'):
    return view.tab_status(message_type="error", message=_("No versions selected"))

if len(request['versions']) == len(adapter.getVersionIds()):
    return view.tab_status(message_type="error", message=_("Can't delete all versions"))
    
result = adapter.deleteVersions(request['versions'])

messages = []
for id, error in result:
    if error is not None:
        msg = _('<span class="error">could not delete ${id}: ${error}</span>')
        msg.mapping = {'id': id, 'error': error}
        messages.append(str(msg))
    else:
        msg = _('deleted ${id}')
        msg.mapping = {'id': id}
        messages.append(str(msg))

return view.tab_status(message_type="feedback", message=', '.join(messages).capitalize())
