## Script (Python) "render_simple"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node
##title=
##
editorsupport = context.service_editorsupport
# find p first (FIXME: inefficient)
for child in node.childNodes:
  if child.nodeType == node.ELEMENT_NODE:
    break
node = child
return '''<textarea cols="20" rows="2" wrap="soft" style="width:100%%;" 
    name="%s">%s</textarea>''' % (node.getNodePath('widget'), 
        editorsupport.replace_xml_entities(editorsupport.render_text_as_editable(node)))
