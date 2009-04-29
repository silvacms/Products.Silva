##parameters=groupids=None
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
deleted_ids = []
not_deleted_ids = []
message_type = 'feedback'

if groupids is None:
    return context.tab_access_groups(message_type="error", message=_("Nothing was selected, so nothing was deleted."))

for id in groupids:
    if model.is_delete_allowed(id):
        deleted_ids.append(id)
    else:
        not_deleted_ids.append(id)
 
model.action_delete(groupids)

if deleted_ids:
    if not_deleted_ids:
        message = _(
            'Deleted ${deleted_ids}, but could not delete ${not_deleted_ids}.',
            mapping={
            'deleted_ids': context.quotify_list(deleted_ids),
            'not_deleted_ids': context.quotify_list(not_deleted_ids)})
    else:
        message = _('Deleted ${deleted_ids}.',
                    mapping={'deleted_ids': context.quotify_list(deleted_ids)})
else:
    message = _('Could not delete ${not_deleted_ids}.',
                mapping={'not_deleted_ids': context.quotify_list(not_deleted_ids)})
    message_type = 'error'

return context.tab_access_groups(message_type=message_type, message=message)
