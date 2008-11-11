from Products.Silva import mangle
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
REQUEST = context.REQUEST

lookup_mode = REQUEST.get('lookup_mode', 0)
return_url = mangle.unquote(REQUEST.get('return_url', ''))
position = REQUEST.get('add_object_position', None)
if position:
    try:
        position = int(position)
    except ValueError:
        position = None

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    if lookup_mode:
        if return_url:
            REQUEST.RESPONSE.redirect(return_url)
        else:
            return context.object_lookup()
    else:
        return model.edit['tab_edit']()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = context.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return context.add_form(message_type="error",
        message=context.render_form_errors(e))

# get id and set up the mangler
id = mangle.Id(model, result['object_id'])
# remove them from result dictionary
del result['object_id']

# try to cope with absence of title in form (happens for ghost)
if result.has_key('object_title'):
    title = result['object_title']
    del result['object_title']
else:
    title = ""

# if we don't have the right id, reject adding
id_check = id.validate()
if id_check == id.OK:
    id = str(id)
else:
    return context.add_form(message_type="error",
        message=context.get_id_status_text(id))

# process data in result and add using validation result
object = context.add_submit_helper(model, id, title, result)

if position is not None and position >= 0:
    model.move_to([object.id], position)

# update last author info in new object
object.sec_update_last_author_info()
model.sec_update_last_author_info()

if lookup_mode:
    if return_url:
        REQUEST.RESPONSE.redirect(return_url)
    else:
        return context.object_lookup()

# now go to tab_edit in case of add and edit, back to container if not.

if return_url:
    REQUEST.RESPONSE.redirect(return_url)
elif REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    message = _(
        "Added ${meta_type} ${id}.",
        mapping={
        'meta_type': object.meta_type,
        'id': context.quotify(id)})
    return model.edit['tab_edit'](message_type="feedback", message=message)
