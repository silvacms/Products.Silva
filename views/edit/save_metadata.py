from Products.Silva.i18n import translate as _

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

if request.form.has_key('renderer_name_select'):
    model.set_renderer_name(request.form['renderer_name_select'])

if all_errors:
    # There were errors...
    type = 'error'
    msg = _('The data that was submitted did not validate properly.')
else:
    type = 'feedback'
    msg = _('Metadata saved.')
    model.sec_update_last_author_info()

return view.tab_metadata(
    form_errors=all_errors,
    message_type=type,
    message=msg)
