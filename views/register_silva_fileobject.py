## Script (Python) "register_silva_fileobject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.register('edit', 'Silva File', ['edit', 'Asset', 'File'])
context.register('public', 'Silva File', ['public', 'File'])
context.register('add', 'Silva File', ['add', 'File'])

return 'Done'
