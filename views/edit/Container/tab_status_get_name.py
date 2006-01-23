## Script (Python) "tab_status_get_name"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model
##title=
##
from Products.Silva.i18n import translate as _
from zope.i18n import translate

if not model.is_default():
    return model.id
else:
    msg = _('${id} of ${parent_id}')
    msg.set_mapping({'id': model.id, 'parent_id': model.get_container().getId()})
    return translate(msg)
