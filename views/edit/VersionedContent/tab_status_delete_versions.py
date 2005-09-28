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
from Products.Silva.adapters.version_management import \
        getVersionManagementAdapter

view = context
request = context.REQUEST
model = request.model
adapter = getVersionManagementAdapter(model)

if not request.has_key('versions'):
    return view.tab_status(message_type="error", 
                            message=_("No versions selected"))

versions = request['versions']
if not same_type(versions, []):
    # request variable is not a list - probably just one checkbox
    # selected.
    versions = [versions,]

if len(versions) == len(adapter.getVersionIds()):
    return view.tab_status(message_type="error", 
                                message=_("Can't delete all versions"))
    
result = adapter.deleteVersions(versions)

messages = []
for id, error in result:
    if error is not None:
        msg = _('could not delete ${id}: ${error}')
        msg.set_mapping({'id': id, 'error': error})
        messages.append(unicode(msg))
    else:
        msg = _('deleted ${id}')
        msg.set_mapping({'id': id})
        messages.append('<span class="error">' + unicode(msg) + '</span>')

return view.tab_status(message_type="feedback", 
                        message=', '.join(messages).capitalize())
