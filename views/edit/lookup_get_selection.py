## Script (Python) "lookup_get_selection"
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

key = ('silva_lookup_selection', context.silva_root())

if not session.has_key(key):
    session[key] = {}

return session[key]
