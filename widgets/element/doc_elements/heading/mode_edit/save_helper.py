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

if request['what'] != 'heading':
    context.element_switch()
    return

data = request['data']
type = request['element_type']

node.get_content().replace_heading(node, data)

# special case of element switching:
if getattr(request,'element_switched',None):
   title = getattr(request,'list_title', None)
   if title:
      doc = node.ownerDocument
      p = doc.createElement('heading')
      node.get_content().replace_heading(p, title)
      node.parentNode.insertBefore(p, node)

node.setAttribute('type', type)
