request = context.REQUEST
node = request.node
parameters = {}

for child in node.childNodes:
    if child.nodeType == child.ELEMENT_NODE:
        if child.nodeName == 'parameter':
            name = child.getAttribute('key').encode('ascii')
            value = child.getAttribute('value').encode('ascii')
            parameters[name] = value

return parameters