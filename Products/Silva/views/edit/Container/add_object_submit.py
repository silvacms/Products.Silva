##parameters=meta_type
# get the add view from the add registry
add_view = context.service_view_registry.get_view('add', meta_type)
# activate submit
return add_view.add_submit()
