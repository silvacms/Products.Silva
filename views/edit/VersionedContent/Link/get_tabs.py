## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# define:
# name, id/None, up_id, toplink_accesskey, tab_accesskey, uplink_accesskey

tabs = [('editor', 'tab_edit', 'tab_edit', '!', '1', '6'),
        ('preview', 'tab_preview', 'tab_preview', '@', '2', '7'),
        ('access', 'tab_access', 'tab_access', '#', '3', '8'),
        ('publish', 'tab_status', 'tab_status', '$', '4', '9'),
       ]

return tabs
