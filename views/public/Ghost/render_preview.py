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
version = model.get_previewable()
result = version.render_preview()
if result is None:
   return "This ghost is broken. (%s)" % version.get_haunted_url()
else:
   return result
