from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error",
                         message=context.render_form_errors(e))
try:
    model.set_image(result['file'])
except IOError, e:
    return view.tab_edit(message_type="error", message=e)
model.sec_update_last_author_info()

return container.tab_edit(message_type="feedback", message="Image uploaded.")

