## Script (Python) "lookup_get_query"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
session = request.SESSION

key = ('silva_lookup_query', context.silva_root())

if not session.has_key(key):
    return None

return session[key]
