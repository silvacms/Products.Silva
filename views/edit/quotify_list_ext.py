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
   return ''
from Products.Silva import mangle
ids = [u'%s (%s)' % (context.quotify(id[0]), unicode(id[1])) for id in ids]
return mangle.List(ids)

