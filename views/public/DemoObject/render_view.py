## Script (Python) "render_view"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
version = model.get_viewable()
if version is None:
   return "There is no public version of this demoObject."
return context.render_helper(version=version)
