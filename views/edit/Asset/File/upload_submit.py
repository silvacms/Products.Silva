## Script (Python) "upload_submit"
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
    result = view.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error",
                         message=context.render_form_errors(e))

file = result['file']
if not file or not getattr(file,'filename',None):
    return view.tab_edit(message_type="error", message="Empty or invalid file.")

model.sec_update_last_author_info()
model.set_file_data(file)

return container.tab_edit(message_type="feedback", message="File uploaded.")
