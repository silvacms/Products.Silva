request = context.REQUEST
model = request.model
view = context

ms = context.service_metadata
editable = model.get_editable()
binding = ms.getMetadata(editable)

values = {}
for set_name in binding.getSetNames():
    values[set_name] = {}
    if request.form.has_key(set_name):
        for key, value in request.form[set_name].items():
            values[set_name][key] = value

all_errors = {}
for set_name in binding.getSetNames():
    errors = binding.setValues(set_name, values[set_name], reindex=1)
    if errors:
        all_errors[set_name] = errors

if all_errors:
    # There were errors...
    type = 'error'
    msg = 'The data submitted did not validate properly.'
else:
    type = 'feedback'
    msg = 'Metadata saved.'

return view.tab_metadata(
    form_errors=all_errors,
    message_type=type,
    message=msg)
