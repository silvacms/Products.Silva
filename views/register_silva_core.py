## Script (Python) "register_silva_core"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# for a clear start, clear the registry entirely (but then all pluggable objects need to be
# registered too)
context.clear()

context.register('edit', 'Silva Folder', ['edit', 'Container', 'Folder'])
context.register('edit', 'Silva Document', ['edit', 'VersionedContent', 'Document'])
context.register('edit', 'Silva Root', ['edit', 'Container', 'Publication'])
context.register('edit', 'Silva Publication', ['edit', 'Container', 'Publication'])
context.register('edit', 'Silva Ghost', ['edit', 'VersionedContent', 'Ghost'])
context.register('edit', 'Silva Image', ['edit', 'Asset', 'Image'])
context.register('edit', 'Silva DemoObject', ['edit', 'VersionedContent', 'DemoObject'])
context.register('edit', 'Silva File', ['edit', 'Asset', 'File'])

context.register('public', 'Silva Folder', ['public', 'Folder'])
context.register('public', 'Silva Publication', ['public', 'Folder'])
context.register('public', 'Silva Document', ['public', 'Document'])
context.register('public', 'Silva Root', ['public', 'Folder'])
context.register('public', 'Silva Ghost', ['public', 'Ghost'])
context.register('public', 'Silva Image', ['public', 'Image'])
context.register('public', 'Silva DemoObject', ['public', 'DemoObject'])
context.register('public', 'Silva File', ['public', 'File'])

context.register('add', 'Silva Folder', ['add', 'Folder'])
context.register('add', 'Silva Publication', ['add', 'Publication'])
context.register('add', 'Silva Document', ['add', 'Document'])
context.register('add', 'Silva Ghost', ['add', 'Ghost'])
context.register('add', 'Silva Image', ['add', 'Image'])
context.register('add', 'Silva DemoObject', ['add', 'DemoObject'])
context.register('add', 'Silva File', ['add', 'File'])

return "done"
