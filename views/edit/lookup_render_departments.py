## Script (Python) "lookup_render_departments"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userinfo
##title=
##
if not userinfo.has_key('ou'):
    return '-'
else:
    return ', '.join(userinfo['ou'])
