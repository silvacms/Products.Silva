
model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Silva.i18n import translate as _
try:
    result = view.layout_form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.tab_metadata(message_type="error",
        message=view.render_form_errors(e))

layout_name = result['layout']
model.set_layout(layout_name)
if layout_name:
    message=_('Layout saved.')
else:
    message=_('Layout has been removed.')

return view.tab_metadata(
    form_errors={},
    message_type='feedback',
    message=message)
