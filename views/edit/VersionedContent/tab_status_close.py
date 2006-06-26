## Script (Python) "tab_status_close"
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

if model.get_public_version() is None:
    return view.tab_status(message_type="error", message=_("There is no public version to close"))

model.close_version()

return view.tab_status(message_type="feedback", message=_("Closed public version."))
