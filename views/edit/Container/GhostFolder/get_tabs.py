## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# dev note: somewhere - maybe here - we should read the user's
# editor preferences and serve the appropriate tab_edit template
#
# define:
# name, id/None, up_id, toplink_accesskey, tab_accesskey, uplink_accesskey
from Products.Silva.i18n import translate as _

tabs = [(_('contents'), 'tab_edit', 'tab_edit', '!', '1', '6'),
        (_('preview'), 'tab_preview', 'tab_preview', '@', '2', '7'),
        (_('properties'), 'tab_metadata', 'tab_metadata', '#', '3', '8'),
        (_('access'), 'tab_access', 'tab_access', '#', '3', '8'),
        (_('publish'), 'tab_status', 'tab_status', '$', '4', '9'),
       ]

return tabs
