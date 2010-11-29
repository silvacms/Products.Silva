## Script (Python) "tab_edit_move_up"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id
##title=
##
from Products.Silva.i18n import translate as _

model = context.REQUEST.model
result = model.move_object_up(id)
if result:
    msg = _("Moved ${id} up.", mapping={'id': context.quotify(id)})
    model.sec_update_last_author_info()
    return context.tab_edit(message_type="feedback", message=msg)
else:
    msg = _("Could not move ${id} up.", mapping={'id': context.quotify(id)})
    return context.tab_edit(message_type="error", message=msg)
