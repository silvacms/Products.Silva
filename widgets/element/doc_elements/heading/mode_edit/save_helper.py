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
editor = context.service_editorsupport

if request['what'] != 'heading':
    context.element_switch()
    return

data = request['data']
type = request['element_type']

editor.replace_heading(node, data)

# special case of element switching:
if getattr(request,'element_switched',None):
   title = getattr(request,'list_title', None)
   if title:
      doc = node.ownerDocument
      p = doc.createElement('heading')
      editor.replace_heading(p, title)
      node.parentNode.insertBefore(p, node)

node.setAttribute('type', node.input_convert(type))
