request = context.REQUEST
session = request.SESSION
model = request.model

key = ('silva_lookup_referer', model.get_root_url())
referer = session[key]

return referer