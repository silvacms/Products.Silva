from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context
ms = context.service_metadata

editable = model.get_editable()
binding = ms.getMetadata(editable)
all_errors = binding.setValuesFromRequest(request, reindex=1)

if all_errors:
    # There were errors...
    type = 'error'
    msg = _(
        'The data that was submitted did not validate properly.  Please adjust '
        'the form values and submit again.')
else:
    type = 'feedback'
    msg = _('Metadata saved.')
    model.sec_update_last_author_info()

templateid = request.form.get('returntotab', 'tab_metadata')
method = getattr(view, templateid)
return method(
    form_errors=all_errors, message_type=type, message=msg)
