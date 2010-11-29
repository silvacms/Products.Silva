## Script (Python) "tab_edit_move_to"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=ids=None,new_position=None
##title=
##
from Products.Silva.i18n import translate as _
from zope.i18n import translate

model = context.REQUEST.model

if ids is None or new_position is None:
    return context.tab_edit(
        message_type="error",
        message=_("Nothing was selected, so nothing was moved."),
        position=new_position)

if new_position.lower() == 'position':
    return context.tab_edit(
        message_type="error",
        message=_("First choose a position number."),
        ids=ids)

actives = []
inactives = []
for id in ids:
    item = model[id]
    if (item.implements_publishable()
    and not (item.implements_content() and item.is_default())):
        actives.append(item.id)
    else:
        inactives.append(item.id)

result = model.move_to(actives, int(new_position)-1)

if result:
    message = _('Object(s) ${ids} moved',
                mapping={'ids': context.quotify_list(actives)})
    message = translate(message)
    if inactives:
        message2 = _(', but could not move ${ids}',
                     mapping={'ids': context.quotify_list(inactives)})
        message += translate(message2)
    model.sec_update_last_author_info()
    return context.tab_edit(message_type="feedback", message=message)
else:
    message = _("Could not move ${ids}.",
                mapping={'ids': context.quotify_list(ids)})
    return context.tab_edit(
        message_type="error",
        message=message)
