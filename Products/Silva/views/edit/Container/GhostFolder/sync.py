## Script (Python) "submit"
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
if model.get_link_status() != model.LINK_OK:
    return context.tab_edit(message_type="error",
        message=_("Ghost Folder was not synchronized, because the target"\
        "is invalid."))
model.haunt()
return context.tab_edit(message_type="feedback",
    message=_("Ghost Folder synchronized"))
