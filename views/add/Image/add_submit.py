from Products.Silva import mangle
from Products.Silva.interfaces import IAsset
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
REQUEST = context.REQUEST

lookup_mode = REQUEST.get('lookup_mode', 0)
return_url = mangle.unquote(REQUEST.get('return_url', ''))

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    if lookup_mode:
        if return_url:
            REQUEST.RESPONSE.redirect(return_url)
        else:
            return context.object_lookup()
    else:
        return context.tab_edit()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = context.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return context.add_form(message_type="error",
        message=context.render_form_errors(e))

id = mangle.Id(model, result['object_id'], file=result['file'],
    interface=IAsset)
file = result['file']

# do some additional validation
if not file or not getattr(file, 'filename', None):
    return context.add_form(message_type="error",
        message=_("Empty or invalid file."))

# if we don't have the right id, reject adding
id_check = id.cook().validate()
if id_check != id.OK:
    return context.add_form(message_type="error",
        message=context.get_id_status_text(id))
id = str(id)

# try to cope with absence of title in form
if result.has_key('object_title'):
    title = result['object_title']
    del result['object_title']
else:
    title = ""

# process data in result and add using validation result

try:
    model.manage_addProduct['Silva'].manage_addImage(id, title, file=file)
except ValueError, e:
    return context.add_form(message_type="error", message='Problem: %s' % e)
object = getattr(model, id)

# update last author info in new object
object.sec_update_last_author_info()

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
    message = _("Added ${meta_type} ${id}.",
                mapping={
                    'meta_type': object.meta_type,
                    'id': context.quotify(id)})
    return context.tab_edit(
        message_type="feedback",
        message=message)
