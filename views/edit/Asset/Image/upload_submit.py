from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error",
                         message=context.render_form_errors(e))

file = result['file']
# do some additional validation
if not file or not getattr(file, 'filename', None):
    return view.tab_edit(message_type="error",
        message="The file is empty or invalid.")

try:
    model.set_image(file)
except IOError, e:
    return view.tab_edit(message_type="error", message='Problem: %s' % e)

model.sec_update_last_author_info()

return container.tab_edit(message_type="feedback", message="Image updated.")

