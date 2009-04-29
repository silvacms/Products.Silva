from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model

try:
    result = context.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error", message=context.render_form_errors(e))

changed = []
old_title = mangle.entities(model.get_title())

model.sec_update_last_author_info()
model.set_title(result['image_title'])

message = _('${old_title} to ${new_title}',
            mapping={
                'old_title': old_title,
                'new_title': mangle.entities(model.get_title())
                })
changed.append(('title', translate(message)))

# is this still in use?
if (model.canScale() and
        result.has_key('web_format') and
        result.has_key('web_scaling')):
    model.set_web_presentation_properties(
        result['web_format'], result['web_scaling'])

message = _("Properties changed: ${changed}",
            mapping={'changed': context.quotify_list_ext(changed)})
return context.tab_edit(message_type="feedback",
    message=message)
