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

if request['what'] != 'p':
    context.element_switch()
    return

# don't need to conver this, later on we will convert it in replace_text()
data = request['data']
type = request['element_type']

# split into number of text items
items = data.strip().split("\r\n\r\n")
# replace text in node
node.get_content().replace_text(node, items[0])
# if necessary, add new paragraphs
if len(items) > 1:
    doc = node.ownerDocument
    next = node.nextSibling
    for item in items[1:]:
        p = doc.createElement('p')
        node.get_content().replace_text(p, item)
        node.parentNode.insertBefore(p, next)

# special case of element switching:
if getattr(request,'element_switched',None):
   title = getattr(request,'list_title', None)
   if title:
      doc = node.ownerDocument
      p = doc.createElement('p')
      p.setAttribute('type','lead')
      node.get_content().replace_heading(p, title)
      node.parentNode.insertBefore(p, node)

node.setAttribute('type', type)
