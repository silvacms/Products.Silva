## Script (Python) "quotify_list_ext"
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
ids = ['%s (%s)' % (context.quotify(id[0]), id[1]) for id in ids]
return context.service_utils.frontend_render_list(ids)
