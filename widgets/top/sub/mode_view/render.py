## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
# only element nodes
childNodes = [child for child in node.childNodes if child.nodeType == child.ELEMENT_NODE]
# nothing, so return empty string
if len(childNodes) == 0:
    return ''
# handle case of starting p or image specially
result = []
firstNode = childNodes[0]

viewer = context.service_editor.getViewer()
if firstNode.nodeName == 'p':
    result.append(context.service_editorsupport.render_text_as_html(firstNode))
elif firstNode.nodeName == 'image':
    result.append(viewer.getWidget(firstNode).tag())
else:
    result.append(viewer.getWidget(firstNode).render())
# handle the rest
for child in childNodes[1:]:
    result.append(viewer.getWidget(child).render())
return ''.join(result)
