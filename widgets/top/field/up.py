## Script (Python) "up"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.node.get_content()
context.REQUEST.SESSION['silva_field_edit_mode'][model.getPhysicalPath()] = 'normal'
context.redirect()
