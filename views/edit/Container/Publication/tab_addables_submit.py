## Script (Python) "tab_addables_submit"
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
form = context.tab_addables_form
changed_metadata = []

try:
    result = form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_addables(
        message_type="error",
        message='%s' % context.render_form_errors(e)
        )

currently_acquired = model.is_silva_addables_acquired()

will_be_acquired = result['acquire_addables']
addables = result['addables']

# if nothing changes, we're done
if will_be_acquired and currently_acquired:
    return context.tab_addables(
        message_type="error",
        message=_("Addable settings have not changed and remain acquired.")
        )

# now update the settings (if we have to)
if will_be_acquired:
    changed_metadata.append(('acquire setting'))
    model.set_silva_addables_allowed_in_publication(None)
else:
    changed_metadata.append(('list of allowed addables'))
    model.set_silva_addables_allowed_in_publication(addables)

message = _("Addable settings changed for: ${changed_metadata}",
            mapping={'changed_metadata': context.quotify_list(changed_metadata)
                     })
return context.tab_addables(message_type="feedback", message=message)
