## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# define name, id, uplink=id/None
return [('Edit', 'tab_edit', 'tab_edit'), 
        ('Preview', 'tab_preview', 'tab_preview'),
        ('Publish', 'tab_status', 'tab_status'),
       ]
