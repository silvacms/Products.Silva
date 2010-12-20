request = context.REQUEST
model = request.model
default = model.get_default() or None

if default is None:
    return ''

return default.view()
