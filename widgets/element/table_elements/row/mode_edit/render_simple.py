## Script (Python) "render_simple"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node
##title=
##
# find p first (FIXME: inefficient)
for child in node.childNodes:
  if child.nodeType == node.ELEMENT_NODE:
    break
node = child
return '<textarea cols="20" rows="2" wrap="soft" style="width:100%%;" name="%s">%s</textarea>' % (node.getNodePath('widget'), node.render_text_as_editable(node))
