model = context.REQUEST.model
parameters = model.parameters()

param = []

for name, (type, default_value, description) in parameters.items():
    param.append('%s : %s : %s : %s' % (type, name, default_value, description))

return '\n'.join(param)