## Script (Python) "save_helper"
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
model = node.get_content()

if request['what'] != 'dlist':
    context.element_switch()
    return

if not request.has_key('element_type'):
    element_type = 'normal'
else:
    element_type = request['element_type']

# don't need to convert it, will do so in replace_text later
data = request['data']

# strip off empty newlines at the end
data = data.rstrip()

list_title = getattr(request,'list_title','')
context.util.save_title(node, list_title)

if element_type not in ['normal', 'compact']:
    return

node.setAttribute('type', element_type)

# remove previous items, except for the title node
childNodes = [ child for child in  node.childNodes if child.nodeName=='dd' or child.nodeName == 'dt']
childNodes.reverse()
for child in childNodes:
    node.removeChild(child)

# now add new items
doc = node.ownerDocument

items = data.split('\r\n\r\n')
for item in items:
    pair = item.split('\r\n')
    dt = doc.createElement('dt')
    model.replace_text(dt, pair[0])
    node.appendChild(dt)
    dd = doc.createElement('dd')
    if len(pair) > 1:
        model.replace_text(dd, pair[1])
    else:
        model.replace_text(dd, '')
    node.appendChild(dd)
