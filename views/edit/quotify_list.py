## Script (Python) "quotify_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids
##title=
##
if not ids:
   return
ids = ['%s' % context.quotify(id) for id in ids]
return context.service_utils.frontend_render_list(ids)
