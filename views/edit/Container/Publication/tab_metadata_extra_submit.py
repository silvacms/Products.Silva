## Script (Python) "tab_metadata_extra_submit"
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
form = context.tab_metadata_extra_form
changed_metadata = []

try:
    result = form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_metadata(message_type="error", message='Input form errors %s' % context.render_form_errors(e))

currently_acquired = model.is_silva_addables_acquired()

will_be_acquired = result['acquire_addables']
addables = result['addables']

# if nothing changes, we're done
if will_be_acquired and currently_acquired:
    return context.tab_metadata(message_type="feedback", message="Addable settings remain acquired.")

# now update the metadata (if we have to)
if will_be_acquired:
    changed_metadata.append(('acquire_addables', 'changed'))
    model.set_silva_addables_allowed_in_publication(None)
else:
    changed_metadata.append(('addables', 'changed'))
    model.set_silva_addables_allowed_in_publication(addables)

return context.tab_metadata(message_type="feedback", message="Addable settings changed for: %s"%(context.quotify_list(changed_metadata)))
