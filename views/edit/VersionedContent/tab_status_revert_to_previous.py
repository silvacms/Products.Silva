## Script (Python) "tab_edit_revert_to_saved"
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
model.sec_update_last_author_info()
view = context
model.revert_to_previous()

return view.tab_status(message_type="feedback", message=_("Reverted to previous version."))
