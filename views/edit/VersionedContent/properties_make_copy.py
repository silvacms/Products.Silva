## Script (Python) "properties_make_copy"
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
model.create_copy()
return view.tab_metadata(message_type="feedback", message=_("New version created."))
