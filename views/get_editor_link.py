## Script (Python) "get_editor_link"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=target
##title=
##
from AccessControl import getSecurityManager
security_manager = getSecurityManager()

tab = 'tab_edit'
if not target.implements_container():    
    if not security_manager.checkPermission('Change Silva content', target):
        tab = 'tab_preview'

return "%s/edit/%s" % (target.absolute_url(), tab)