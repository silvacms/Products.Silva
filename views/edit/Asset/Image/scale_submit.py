from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.scale_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg = ['Scaling and/or format changed']
msg_type = 'feedback'

if model.canScale():
    model.set_web_presentation_properties(
        result['web_format'], result['web_scaling'])
    
return view.tab_edit(message_type=msg_type, message=' '.join(msg))
