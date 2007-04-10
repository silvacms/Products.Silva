## Script (Python) "tab_status_get_name"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=meta_type
##title=
##
from Products.Silva.i18n import translate as _

msg = _('modify ${meta_type}', mapping={'meta_type': meta_type})
return msg
