## Script (Python) "render_field"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, info
##title=
##
if context.is_field_simple(node):
  # find p first (FIXME: inefficient)
  for child in node.childNodes:
    if child.nodeType == node.ELEMENT_NODE:
      break
  node = child
  if len(node.childNodes) == 0:
      return '<td align="%s" width="%s">&nbsp;</td>' % (info['align'], info['html_width'])
  if len(node.childNodes) == 1 and len(node.childNodes[0].data.strip()) == 0:
      return '<td align="%s" width="%s">&nbsp;</td>' % (info['align'], info['html_width'])
  else:
      return '<td align="%s" width="%s">%s</td>' % (info['align'], info['html_width'], node.render_text_as_html(node))
else:
  context.service_editor.setViewer('service_sub_previewer')
  content = context.service_editor.getViewer().getWidget(node).render()
  return '<td align="%s" width="%s">%s</td>' % (info['align'], info['html_width'], content)
