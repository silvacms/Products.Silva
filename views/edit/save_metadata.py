request = context.REQUEST
model = request.model
view = context

ms = context.service_metadata
editable = model.get_editable()
binding = ms.getMetadata(editable)

all_errors = {}
for set_name in binding.getSetNames():
    errors = binding.setValuesFromRequest(set_name, request, reindex=1)
    if errors:
        all_errors[set_name] = errors

return view.tab_metadata(form_errors=all_errors)