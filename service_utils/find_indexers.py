container_types = ['Silva Folder', 'Silva Publication',]
idx_types = ['Silva Indexer',]

foo = []
def recurse_into_folder(folder, dpth=0):
    objs = folder.objectValues(idx_types)
    for obj in objs:
        foo.append('--> Indexer found: %s/edit/' % (obj.absolute_url() ))   
    for subfolder in folder.objectValues(container_types):
        recurse_into_folder(subfolder, dpth+1)

recurse_into_folder(context.get_root())
return '\n'.join(foo)