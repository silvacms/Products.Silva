## Script (Python) "tab_status_view_versions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Revoke approval of approved content
##
from Products.Silva.i18n import translate as _

view = context
request = view.REQUEST
model = request.model

if not request.has_key('versions'):
    return view.tab_status(message_type='error', 
        message=_("You didn't select any versions."))

versions = request['versions']
if len(versions) != 2:
    return view.tab_status(message_type='error',
        message=_('Please select exactly two versions.'))

return view.tab_status_view_versions(
          version1=getattr(context, versions[0]),
          version2=getattr(context, versions[1]))
