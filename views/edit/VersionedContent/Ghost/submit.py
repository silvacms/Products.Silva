## Script (Python) "submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content_url
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context
if context.REQUEST.has_key('add_cancel'):
    return view.tab_edit()
model.sec_update_last_author_info()
model.get_editable().set_haunted_url(content_url)
return view.tab_edit(message_type="feedback", message=_("Ghost changed."))
