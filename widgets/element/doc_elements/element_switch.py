## Script (Python) "element_switch"
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

what = request['what']

# can't submit/switch to elements not known
if what not in ['pre', 'p', 'heading', 'list', 'dlist']:
    return

nodeName = node.nodeName

# remove old element and create new one of right type 
doc = node.ownerDocument
parent = node.parentNode
next = node.nextSibling
parent.removeChild(node)
new = doc.createElement(what)
parent.insertBefore(new, next)
node = new

# now focus the node
service_editor = context.service_editor

service_editor.setNodeWidget(node, 
  context.get_widget_path()[:-2] + (what, 'mode_edit'))

widget = service_editor.getWidget(node)

request.set('element_switched', 1)

# initialize new widget
widget.insert_init()
# now call submit on the node we are editing
widget.save_helper()
# put it in done_mode
widget.done_mode()
request.set('element_switched', 1)
