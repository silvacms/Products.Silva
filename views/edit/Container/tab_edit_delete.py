## Script (Python) "tab_edit_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=
##
model = context.REQUEST.model
view = context
deleted_ids = []
not_deleted_ids = []
message_type = 'feedback'

if ids is None:
    return view.tab_edit(message_type="error", message="Nothing was selected, so nothing was deleted.")

for id in ids:
    if model.is_delete_allowed(id):
        deleted_ids.append(id)
    else:
        not_deleted_ids.append(id)
 
model.action_delete(ids)

if deleted_ids:
    if not_deleted_ids:
        message = 'Deleted %s, <span class="error">but could not delete %s. Probably there is a published version that must be closed, or an approved version that needs to be revoked. Change the status in the Publish screen (alt-5).</span>' % (view.quotify_list(deleted_ids),
            view.quotify_list(not_deleted_ids))
    else:
        message = 'Deleted %s.' % view.quotify_list(deleted_ids)
else:
    message = 'Could not delete %s. Possibly there is a published version, which must be closed before it can be deleted. Or, the document is approved (the link will be green), and approval needs to be revoked. Change the status in the Publish screen (alt-5).' % view.quotify_list(not_deleted_ids)
    message_type = 'error'

return view.tab_edit(message_type=message_type, message=message)
