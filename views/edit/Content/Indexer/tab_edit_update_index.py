## Script (Python) "tab_edit_update_index"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

indexer = context.REQUEST.model
view = context
indexer.update()
return view.tab_edit(message_type='feedback', message=_("Index updated"))
