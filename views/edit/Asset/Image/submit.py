from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

model.sec_update_last_author_info()
model.set_title(model.input_convert(result['image_title']))

msg = ['Properties changed']
msg_type = 'feedback'

# is this still in use?
if (model.canScale() and 
        result.has_key('web_format') and 
        result.has_key('web_scaling')):
    model.set_web_presentation_properties(
        result['web_format'], result['web_scaling'])
    
return view.tab_edit(message_type=msg_type, message=' '.join(msg))
