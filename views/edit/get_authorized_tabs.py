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
    if container.REQUEST.other['model'].implements_container():
        return [('contents', 'tab_edit', 'tab_edit', '!', '1', '6'), 
                ('preview', 'tab_preview', 'tab_preview', '@', '2', '7'),
               ]
    else:
        # readers cannot change content object, just preview it
        return [ ('preview', 'tab_preview', 'tab_preview', '@', '2', '7') ]
else:
    return context.get_tabs()
