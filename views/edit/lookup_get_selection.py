request = context.REQUEST
session = request.SESSION

key = ('silva_lookup_selection', context.silva_root())

if not session.has_key(key):
    session[key] = {}

# Hack to get SESSION transaction/persistency correct
session[key] = session[key]

return session[key]