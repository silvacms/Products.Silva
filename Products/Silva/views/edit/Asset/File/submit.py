## Script (Python) "upload_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##parameters=
##title=
##

from Products.Silva import mangle
from Products.Formulator.Errors import FormValidationError
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model

try:
    result = context.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error",
        message=context.render_form_errors(e))

changed = []
old_title = mangle.entities(model.get_title())

model.set_title(result['file_title'])

message = _('${old_title} to ${new_title}',
            mapping={
                'old_title': old_title,
                'new_title': mangle.entities(model.get_title())
                })
changed.append(('title', translate(message)))

# FIXME: should put in message
# XXX: I don't understand the FIXME message.
message = _("Properties changed: ${changed}",
            mapping={'changed': context.quotify_list_ext(changed)})
return context.tab_edit(message_type="feedback", message=message)
