## Script (Python) "register_silva_ing"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# container.clear()

context.register('edit', 'Silva ING Zittingsdag', ['edit', 'VersionedContent', 'Zittingsdag'])
context.register('public', 'Silva ING Zittingsdag', ['public', 'Zittingsdag'])
context.register('add', 'Silva ING Zittingsdag', ['add', 'Zittingsdag'])

return "Done ING"
