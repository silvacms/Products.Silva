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
request = context.REQUEST

version = model.get_previewable()
if version is None:
   return "There is no public version of this demoObject."

return context.render_helper(version=version)
