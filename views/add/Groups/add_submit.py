#Almost identical to add_submit in the add views,
# but no other way to override then to copy code *ugh*.

from Products.Silva.helpers import check_valid_id, IdCheckValues

model = context.REQUEST.model
view = context
REQUEST = context.REQUEST
groups_service = context.service_groups

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    return model.edit['tab_access_groups']()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.add_form(message_type="error", message=view.render_form_errors(e))

# get id and title from form, convert title to unicode
id = result['object_id'].encode('ascii', 'replace')
# remove them from result dictionary
del result['object_id']

# try to cope with absence of title in form (happens for ghost)
if result.has_key('object_title'):
    title = result['object_title']
    del result['object_title']
else:
    title = ""

# if we don't have the right id, reject adding
id_check = check_valid_id(model, id)
if not id_check == IdCheckValues.ID_OK:
    return view.add_form(message_type="error", message=view.get_id_status_text(id, id_check))

if groups_service.isGroup(id):
    return view.add_form(
        message_type="error", 
        message=\
"""There's already a (Virtual) Group with the name %s in this Silva site. 
<br />
<br />
In contrast to other Silva Objects, (Virtual) Group IDs must be unique 
within a complete Silva instance.""" % view.quotify(id))

# process data in result and add using validation result
object = context.add_submit_helper(model, id, title, result)

# update last author info in new object
object.sec_update_last_author_info()

# now go to tab_edit in case of add and edit, back to container if not.
return model.edit['tab_access_groups'](
    message_type="feedback", 
    message="Added %s %s." % (object.meta_type, view.quotify(id)))
