## Script (Python) "demoObject_submit"
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

# Validate the form
try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=view.render_form_errors(e))

# Add the results to the object
info = result['info']
number = result['number']
date = result['date']

model.set_title(model.input_convert(result['object_title']))
model.get_editable().set_demo_data(info, number, date)
model.sec_update_last_author_info()

# And return a message
return view.tab_edit(message_type="feedback", message="DemoObject data changed")
