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

model = context.REQUEST.model
view = context

# we might be called 'accidentally' if after creating a new copy the editor
# does a client-side reload of the current URL (after a save or something),
# in that case just return tab_edit
if model.get_editable():
    return view.tab_edit()

model.sec_update_last_author_info()
model.create_copy()
return view.tab_edit(message_type="feedback", message=_("New version created."))
