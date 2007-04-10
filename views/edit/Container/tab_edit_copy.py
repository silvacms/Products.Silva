## Script (Python) "tab_edit_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
view = context

if ids is None:
    return view.tab_edit(message_type="error", message=_("Nothing was selected, so nothing was copied."))

model.action_copy(ids, context.REQUEST)
message = _("Placed ${ids} on the clipboard for copying.",
            mapping={'ids': view.quotify_list(ids)})
return view.tab_edit(message_type="feedback", message=message)
