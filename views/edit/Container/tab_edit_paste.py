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

if not context.REQUEST.has_key('__cp'):
    return view.tab_edit(message_type="error", _(message="No content available to paste."))

message = model.action_paste(context.REQUEST)
return view.tab_edit(message_type="feedback", message=message)
