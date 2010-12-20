## Script (Python) "tab_edit_make_copy"
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

came_from_view = request.get('came_from_view', 'tab_edit')
view = model.edit[came_from_view]

# we might be called 'accidentally' if after creating a new copy the editor
# does a client-side reload of the current URL (after a save or something),
# in that case just return tab_edit
if model.get_next_version():
    return view()

model.sec_update_last_author_info()
model.create_copy()

# if user is in the editor screen and making a new version, return to edit
if came_from_view == 'tab_edit_make_copy':
    request.RESPONSE.redirect('%s/edit' % (model.absolute_url()))
    return ''

return view(message_type="feedback", message=_("New version created."))
