## Script (Python) "get_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node

datasource = context.get_datasource()
if not datasource:
    return None

datasource_parameters = datasource.parameters()
current = context.get_parameters()

form = datasource.parameter_values_as_form(current)
return form