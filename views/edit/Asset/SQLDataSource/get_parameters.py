## Script (Python) "parameters"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

model = context.REQUEST.model
parameters = model.parameters()

param = []

for name, (type, default_value, description) in parameters.items():
    param.append('%s : %s : %s : %s' % (type, name, default_value, description))

return '\n'.join(param)