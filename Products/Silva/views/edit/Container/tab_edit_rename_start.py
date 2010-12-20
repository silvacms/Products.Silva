## Script (Python) "tab_edit_rename_start"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.i18n import translate as _

if not context.REQUEST.has_key('ids') or not context.REQUEST['ids']:
    return context.tab_edit(message_type='error', message=_('Nothing was selected, so nothing can be renamed.'))
else:
    return context.tab_edit_rename()
