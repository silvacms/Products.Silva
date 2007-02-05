from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model
view = context

try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error",
        message=context.render_form_errors(e))

changed = []
old_title = mangle.entities(model.get_title())

model.sec_update_last_author_info()
model.set_title(result['file_title'])

message = _('${old_title} to ${new_title}')
message.set_mapping({
    'old_title': old_title,
    'new_title': mangle.entities(model.get_title())
    })
changed.append(('title', translate(message)))

# FIXME: should put in message
# XXX: I don't understand the FIXME message.
message = _("Properties changed: ${changed}")
message.set_mapping({'changed': context.quotify_list_ext(changed)})
return view.tab_edit(message_type="feedback", 
    message=message)
