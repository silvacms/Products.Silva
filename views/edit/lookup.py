request = context.REQUEST
session = request.SESSION
model = request.model

key = ('silva_lookup_referer', model.get_root_url())
default_referer = context.tab_access.absolute_url()
referer = request.get('HTTP_REFERER', default_referer)

session[key] = referer

request.RESPONSE.redirect('%s/edit/tab_access_lookup' % model.absolute_url())