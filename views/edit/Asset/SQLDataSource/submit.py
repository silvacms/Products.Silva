## Script (Python) "submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context

try:
    result = view.properties_form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=context.render_form_errors(e))

changed = []
old_title = model.get_title_html()

model.sec_update_last_author_info()
model.set_title(model.input_convert(result['file_title']))

changed.append(('title', '%s to %s' % (old_title, model.get_title_html())))

# FIXME: should put in message
return view.tab_edit(message_type="feedback", message="Properties changed: %s" % (context.quotify_list_ext(changed)))
