## Script (Python) "get_parameters"
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
parameters = {}

for child in node.childNodes:
    if child.nodeType == child.ELEMENT_NODE:
        if child.nodeName == 'parameter':
            name = child.getAttribute('key')
            value = child.getAttribute('value')
            parameters[name] = value

return parameters