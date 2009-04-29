request = context.REQUEST
session = request.SESSION
model = request.model

key = ('silva_lookup_selection', model.get_root_url())

if not session.has_key(key):
    session[key] = {}

# Hack to get SESSION transaction/persistency correct
session[key] = session[key]

return session[key]