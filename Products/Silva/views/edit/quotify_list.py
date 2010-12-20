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
   return ''
from Products.Silva import mangle
ids = [context.quotify(id) for id in ids]
return mangle.List(ids)

