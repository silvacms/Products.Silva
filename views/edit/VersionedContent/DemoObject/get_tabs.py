## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# define name, id, up_id=id/None
return [('Edit', 'tab_edit', 'tab_edit'),
        ('Preview', 'tab_preview', 'tab_preview'),
        ('Access', 'tab_access', 'tab_access'),
        ('Publish', 'tab_status', 'tab_status'),
       ]
