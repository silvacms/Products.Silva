## Script (Python) "register_silva_index"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# FIXME: First clear the registry?
# container.clear()

context.register('edit', 'Silva Index', ['edit', 'Content', 'Index'])
context.register('public', 'Silva Index', ['public', 'Index'])
context.register('add', 'Silva Index', ['add', 'Index'])

return "Done"
