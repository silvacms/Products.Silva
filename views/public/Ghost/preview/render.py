## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
version = context.REQUEST.model
result = version.render_view()
if result is None:
   return "This ghost is broken. (%s)" % version.get_haunted_url()
else:
   return result
