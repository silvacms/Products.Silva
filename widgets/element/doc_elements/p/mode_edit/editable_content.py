## Script (Python) "editable_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
editorsupport = context.service_editorsupport
return editorsupport.render_text_as_editable(node)
