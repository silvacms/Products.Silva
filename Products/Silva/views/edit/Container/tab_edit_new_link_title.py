## Script (Python) "tab_edit_new_link_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=addable_name
##title=
#
from Products.Silva.i18n import translate as _
msg = _('Create a ${addable_name}', mapping={'addable_name': addable_name})
return msg
