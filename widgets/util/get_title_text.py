## Script (Python) "get_title_text"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, html_encoded=None
##title=helper: get the rendered content of the <title> tag
##
editorsupport = context.service_editorsupport
for child in node.childNodes:
  if child.nodeName=='title':
     if html_encoded:
       return editorsupport.render_heading_as_html(child)
     else:
       return editorsupport.render_heading_as_editable(child)

return ''
