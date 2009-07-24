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
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

try:
    result = view.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error",
                         message=context.render_form_errors(e))

file = result['file']
if not file or not getattr(file,'filename',None):
    return view.tab_edit(
        message_type="error", 
        message=_("Empty or invalid file.")
        )

if not ('.' in file.filename):
    return view.tab_edit(
        message_type="error",
        message=_("Please upload a file with an correct extension."))

model.sec_update_last_author_info()
model.set_file_data(file)

message_type=REQUEST.form.get('message_type', 'feedback')
message=_("File uploaded.")
if REQUEST.form.has_key('message'):
    message = _(REQUEST.form['message'])

return container.tab_edit(
    message_type=message_type,
    message=message
    )
