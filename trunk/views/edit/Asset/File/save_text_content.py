## Script (Python) "save_text_content"
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
REQUEST = context.REQUEST

try:
    result = context.text_edit_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error",
                         message=context.render_form_errors(e))

text = result['text']

model.sec_update_last_author_info()
model.set_text_file_data(text)

message_type=REQUEST.form.get('message_type', 'feedback')
message=_("File uploaded.")
if REQUEST.form.has_key('message'):
    message = _(REQUEST.form['message'])

return container.tab_edit(
    message_type=message_type,
    message=message
    )
