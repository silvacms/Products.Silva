## Script (Python) "get_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
mode = context.id.split('_')[-1]
if mode not in ['done', 'insert', 'edit', 'normal']:
    return 'unknown'
else:
    return mode
