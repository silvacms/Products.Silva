## Script (Python) "get_authorized_tabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
if not context.get_silva_permissions()['ChangeSilvaContent']:
    return [('Edit', 'tab_edit', 'tab_edit'), 
            ('Preview', 'tab_preview', 'tab_preview'),
           ]
else:
    return context.get_tabs()
