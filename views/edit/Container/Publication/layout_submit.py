
model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.layout_form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.tab_metadata(message_type="error",
        message=view.render_form_errors(e))

model.set_layout(result['layout'])

return view.tab_metadata(
    form_errors={},
    message_type='feedback',
    message='Layout saved')
