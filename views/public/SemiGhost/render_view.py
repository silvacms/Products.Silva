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
  return "Sorry, this document is not published yet."
result = version.render_view()
if result is None:
   return "There is no published content in this container yet."
else:
   return result
