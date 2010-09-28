from Products.Formulator.Errors import FormValidationError
from Products.Silva.i18n import translate as _

model = context.REQUEST.model

try:
    result = context.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(
        message_type="error", message=context.render_form_errors(e))

file = result['file']
# do some additional validation
if not file or not getattr(file, 'filename', None):
    return context.tab_edit(message_type="error",
        message=_("The file is empty or invalid."))

try:
    model.set_image(file)
except ValueError, e:
    message = _('Problem: ${errors}', mapping={'errors': e})
    return context.tab_edit(message_type="error", message=message)

model.sec_update_last_author_info()

return container.tab_edit(
    message_type="feedback",
    message=_("Image updated."))
