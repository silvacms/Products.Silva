## Script (Python) "lookup_use_selection"
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

referer = session.get('referer', 'tab_access')
session['referer'] = None
del session['referer']

return getattr(context, referer)()
