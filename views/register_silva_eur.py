## Script (Python) "register_silva_eur"
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

context.register('edit', 'Silva Course', ['edit', 'VersionedContent', 'Course'])
context.register('public', 'Silva Course', ['public', 'Course'])
context.register('add', 'Silva Course', ['add', 'Course'])

context.register('edit', 'Silva FAQ', ['edit', 'Content', 'FAQ'])
context.register('public', 'Silva FAQ', ['public', 'FAQ'])
context.register('add', 'Silva FAQ', ['add', 'FAQ'])

context.register('edit', 'Silva EUR Resolution', ['edit', 'VersionedContent', 'EurResolution'])
context.register('public', 'Silva EUR Resolution', ['public', 'EurResolution'])
context.register('add', 'Silva EUR Resolution', ['add', 'EurResolution'])

context.register('edit', 'Silva EUR Meeting', ['edit', 'Container', 'EurMeeting'])
context.register('public', 'Silva EUR Meeting', ['public', 'EurMeeting'])
context.register('add', 'Silva EUR Meeting', ['add', 'EurMeeting'])

return "Done"
