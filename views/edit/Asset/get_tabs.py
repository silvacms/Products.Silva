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
tabs = [('Editor', 'tab_edit', 'tab_edit', '!', '1', '6'),
        ('Preview', 'tab_preview', 'tab_preview', '@', '2', '7'),
        ('Metadata', 'tab_metadata', 'tab_metadata', '#', '3', '8'),
        ('Access', 'tab_access', 'tab_access', '$', '4', '9'),
       ]

return tabs
