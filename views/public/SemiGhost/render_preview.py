## Script (Python) "render_preview"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
result = model.render_preview()
if result is None:
   return "There is no published content in this container."
else:
   return result
