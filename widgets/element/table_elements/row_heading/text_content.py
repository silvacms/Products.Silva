## Script (Python) "text_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
return context.service_editorsupport.render_heading_as_html(node)
