## Script (Python) "get_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# define name, id, up_id
tabs = [('Edit', 'tab_edit', 'tab_edit'),
        ('Preview', 'tab_preview', 'tab_preview'),
       ]

if hasattr(context, 'service_docma'):
    tabs.append(('Docma', 'tab_docma', 'tab_docma'))

tabs += [('Metadata', 'tab_metadata', 'tab_metadata'),
         ('Access', 'tab_access', 'tab_access'),
         ('Publish', 'tab_status', 'tab_status'),
        ]

return tabs
