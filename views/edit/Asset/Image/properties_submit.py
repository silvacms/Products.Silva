## Script (Python) "properties_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.properties_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))
model.sec_update_last_author_info()
model.set_title(model.input_convert(result['image_title']))
# FIXME: should put in message
return view.tab_edit(message_type="feedback", message="Properties changed.")
