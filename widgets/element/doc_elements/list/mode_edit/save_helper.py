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
editorsupport = context.service_editorsupport

if request['what'] != 'list':
    context.element_switch()
    return

# don't need to convert it, will do so in replace_text later
data = request['data']

# strip off trailing whitespace, so empty lines do not lead to empty listitems
data = data.rstrip()

if not request.has_key('element_type'):
    element_type = 'disc'
else:
    element_type = request['element_type']

if element_type not in ['circle', 'square', 'disc', 
                        '1', 'A', 'a', 'I', 'i', 'none']:
    return

node.setAttribute('type', node.input_convert(element_type))

# remove previous items, except for the title node
childNodes = [ child for child in  node.childNodes if child.nodeName=='li' ]
childNodes.reverse()
for child in childNodes:
    node.removeChild(child)

# now add new items
doc = node.ownerDocument

items = data.split('\r\n\r\n')
for item in items:
   li = doc.createElement('li')
   editorsupport.replace_text(li, item)
   node.appendChild(li)
