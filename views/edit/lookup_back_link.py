request = context.REQUEST
session = request.SESSION

key = ('silva_lookup_referer', context.silva_root())
referer = session[key]

return referer