##parameters=meta_type
# get the add view from the add views registry
request = context.REQUEST
if not meta_type:
    if request.has_key('meta_type'):
        meta_type = request['meta_type']
if meta_type=='None':
    return context.tab_edit_new()
add_view = context.service_view_registry.get_view('add', meta_type)
return add_view.add_form()
