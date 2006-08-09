## Script (Python) "tab_edit_revoke_approval"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model

came_from_view = request.get('came_from_view', 'tab_edit_revoke_approval')
view = model.edit[came_from_view]

model.unapprove_version()

# if user is in the editor screen and approving, return to edit/tab_edit
if came_from_view == 'tab_edit_revoke_approval':
    request.RESPONSE.redirect('%s/edit/tab_edit' % (model.absolute_url()))
    return ''
    
return view(message_type="feedback", message=_("Revoked approval."))
