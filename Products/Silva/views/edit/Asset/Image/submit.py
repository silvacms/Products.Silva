from Products.Silva import mangle
from Products.Formulator.Errors import FormValidationError
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model

try:
    result = context.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(
        message_type="error", message=context.render_form_errors(e))


model.sec_update_last_author_info()
model.set_title(result['image_title'])

return context.tab_edit(message_type="feedback",  message=_("Changes saved."))
