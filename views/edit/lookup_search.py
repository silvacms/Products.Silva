## Script (Python) "lookup_search"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=name
##title=
##
request = context.REQUEST
session = request.SESSION
model = request.model
view = context

key1 = ('silva_lookup_query', context.silva_root())
key2 = ('silva_lookup_search_result', context.silva_root())

name = name.strip()

if name == '':
    return view.tab_access_lookup(message_type="error", message="No search string supplied.")

if len(name) < 3:
    return view.tab_access_lookup(message_type="error", message="Search string '%s' is too short. Please try a longer search string." % name)       

if name != view.lookup_get_query():
    session[key1] = name
    session[key2] = model.sec_find_users(name)

if len(session[key2]) == 0:
    return view.tab_access_lookup(message_type="feedback", message="No users found for search string '%s'." % name)

return view.tab_access_lookup(message_type="feedback", message="Searched for '%s'." % name)
