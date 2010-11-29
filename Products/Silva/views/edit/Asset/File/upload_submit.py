## Script (Python) "upload_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##bind view=view
##parameters=
##title=
##
from Products.Formulator.Errors import FormValidationError
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
REQUEST = context.REQUEST

try:
    result = context.upload_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error",
                         message=context.render_form_errors(e))

uploaded_file = result['file']
if not uploaded_file or not getattr(uploaded_file,'filename',None):
    return context.tab_edit(
        message_type="error",
        message=_("Empty or invalid file."))

model.set_file_data(uploaded_file)

message_type=REQUEST.form.get('message_type', 'feedback')
message=_("File uploaded.")
if REQUEST.form.has_key('message'):
    message = _(REQUEST.form['message'])

return container.tab_edit(
    message_type=message_type,
    message=message
    )
