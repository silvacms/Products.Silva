## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
service_editor = context.service_editor
viewer = context.service_editor.getViewer()
texts = [service_editor.renderView(child) for child in node.childNodes if 
         child.nodeType == node.ELEMENT_NODE and child.nodeName == 'li']
if node.hasAttribute('type'):
    type = node.getAttribute('type')
else:
    type = 'disc'
return context.util.render_list(type, texts)
