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
        ('Groups', None, 'tab_access_groups', '@', '2', '7'),
       ]

return tabs
