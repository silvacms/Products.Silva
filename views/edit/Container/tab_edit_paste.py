## Script (Python) "tab_edit_paste"
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

if not context.REQUEST.has_key('__cp') or context.REQUEST['__cp'] is None:
    return view.tab_edit(message_type="error", message=_("No content available to paste."))

message_type, message = model.action_paste(context.REQUEST)
model.sec_update_last_author_info()
return view.tab_edit(message_type=message_type, message=message)
