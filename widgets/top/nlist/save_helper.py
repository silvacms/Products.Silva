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

node.setAttribute('type', node.input_convert(request['element_type']))

# process all elements (note that we make a tuple of childNodes so it won't change anymore,
# even if we insert stuff)
for child in tuple(node.childNodes):
   if child.nodeType != node.ELEMENT_NODE:
       continue
   if child.nodeName == 'title': continue
   try:
       data = request[child.getNodePath('widget')]
       context.set_simple_content(child, data)
   except KeyError:
       pass
