from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model
view = context

try:
    result = view.scale_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

msg = _('Scaling and/or format changed')
msg_type = 'feedback'

if model.canScale():
    try:
        model.set_web_presentation_properties(
            result['web_format'], result['web_scaling'], result['web_crop'])
    except ValueError, e:
        msg = unicode(e)
        msg_type = 'error'
    
return view.tab_edit(message_type=msg_type, message=msg)
