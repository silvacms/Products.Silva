## Script (Python) "submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content_url=None
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
if context.REQUEST.has_key('add_cancel'):
    return context.tab_edit()
model.set_haunted_url(content_url)
if model.get_link_status() != model.LINK_OK:
    return context.tab_edit(message_type="warning",
        message=_("Ghost Folder changed but not synchronized, because the"\
        "new target is invalid."))
model.haunt()
return context.tab_edit(
    message_type="feedback",
    message=_("Ghost Folder changed.")
    )
