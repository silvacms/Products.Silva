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
current = {}

for child in node.childNodes:
    if child.nodeType == child.ELEMENT_NODE:
        if child.nodeName == 'parameter':
            name = child.getAttribute('key')
            value = child.getAttribute('value')
            current[name] = value

form = datasource.parameter_values_as_form(current)
return form