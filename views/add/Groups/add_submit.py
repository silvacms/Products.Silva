#Almost identical to add_submit in the add views,
# but no other way to override than to copy code *ugh*.

from Products.Silva import mangle
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context
REQUEST = context.REQUEST
groups_service = context.service_groups

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return model.edit['tab_access_groups'](message_type="error", message=view.render_form_errors(e))

# get id and title from form, convert title to unicode
id = mangle.Id(model, result['object_id'])
# remove them from result dictionary
del result['object_id']

# try to cope with absence of title in form (happens for ghost and groups)
if result.has_key('object_title'):
    title = result['object_title']
    del result['object_title']
else:
    title = ""

# if we don't have the right id, reject adding
id_check = id.validate()
if not id_check == id.OK:
    return model.edit['tab_access_groups'](message_type="error",
        message=view.get_id_status_text(id))

if groups_service.isGroup(str(id)):
    message=_("""There's already a Group with the name ${id} in this Silva
        site.<br />In contrast to other Silva objects, Group IDs must be
        unique within a Silva instance.""", mapping={'id': view.quotify(id)})
    return model.edit['tab_access_groups'](
        message_type="error", 
        message=message
        )

id = str(id)

# process data in result and add using validation result
object = context.add_submit_helper(model, id, title, result)

# update last author info in new object
object.sec_update_last_author_info()

# now go to the edit screen in case of add and edit, back to groups if not.
if REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    message = _("Added ${meta_type} ${id}.",mapping={'meta_type': object.meta_type,'id': view.quotify(id)})
    return model.edit['tab_access_groups'](
        message_type="feedback", 
        message=message
        )
