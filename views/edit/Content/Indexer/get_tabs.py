## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# name, id/None, up_id, toplink_accesskey, tab_accesskey, uplink_accesskey
tabs = [('Edit', 'tab_edit', 'tab_edit', '!', '1', '6'),
        ('Preview', 'tab_preview', 'tab_preview', '@', '2', '7'),
        ('Access', 'tab_access', 'tab_access', '$', '3', '8'),
       ]

return tabs
