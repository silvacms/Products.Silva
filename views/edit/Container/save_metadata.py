# This is a first evolutionary step towards improved
# default content and folder title handling...
# ...and it is rather ugly for now.

request = context.REQUEST
model = request.model
view = context

ms = context.service_metadata
editable = model.get_editable()
binding = ms.getMetadata(editable)

values = {}
for set_name in binding.getSetNames():
    if set_name == 'silva-content':
        # don't do the title/short_title for Folder w/metadata (yet),
        # but set it manually.
        title = request.form['silva-content']['maintitle']
        short_title = request.form['silva-content']['shorttitle']
        model.set_title(title)
        model.set_short_title(short_title)
        continue
    values[set_name] = {}
    for key, value in request.form[set_name].items():
        values[set_name][key] = value

all_errors = {}
for set_name in binding.getSetNames():
    if set_name == 'silva-content':
        # don't do the title/short_title for Folder w/metadata (yet),
        # it is set manually.
        continue
    errors = binding.setValues(set_name, values[set_name], reindex=1)
    if errors:
        all_errors[set_name] = errors

if all_errors:
    # There were errors...
    type = 'warning'
    msg = 'Metadata input had validation errors.'
else:
    type = 'feedback'
    msg = 'Metadata saved.'

return view.tab_metadata(
    form_errors=all_errors,
    message_type=type,
    message=msg)
