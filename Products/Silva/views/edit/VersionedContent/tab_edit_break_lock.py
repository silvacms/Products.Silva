## Script (Python) "tab_edit_break_lock"
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
model.sec_break_lock()
return context.tab_edit(message_type="feedback", message=_("Lock broken"))
