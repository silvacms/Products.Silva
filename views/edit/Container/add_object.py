##parameters=meta_type
# get the add view from the add views registry
add_view = context.service_view_registry.get_view('add', meta_type)
return add_view.add_form()
