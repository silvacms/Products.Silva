## Script (Python) "lookup"
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

referer = request.form.get('referer', 'tab_access')
session['referer'] = referer

return context.tab_access_lookup()
