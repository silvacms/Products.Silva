## Script (Python) "tab_status_get_name"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id
##title=
##
from Products.Silva.i18n import translate as _

msg = _('preview ${id}')
msg.set_mapping({'id': id})
return msg
