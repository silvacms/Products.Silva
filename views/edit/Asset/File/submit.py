from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError

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

changed.append(('title', '%s to %s' % (old_title,
    mangle.entities(model.get_title()))))

# FIXME: should put in message
# XXX: I don't understand the FIXME message.
return view.tab_edit(message_type="feedback", 
    message="Properties changed: %s" % (context.quotify_list_ext(changed)))
