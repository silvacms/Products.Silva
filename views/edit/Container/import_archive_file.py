from Products.Silva.adapters import archivefileimport, zipfileimport

view = context
request = view.REQUEST
model = request.model

archive = request.get('importfile', None)
if archive is None or not archive:
    return view.tab_edit_import(
        message_type='error', message='Select a file for upload.')
        

recreate = request.get('recreate_dirs', None)
title = unicode(request.get('title', ''), 'utf-8')
importer = zipfileimport.getZipfileImportAdapter(model)
fullmedia = importer.isFullmediaArchive(archive)

try:
    if fullmedia:
        succeeded, failed = importer.importFromZip(model, archive)
    else:
        importer = archivefileimport.getArchiveFileImportAdapter(model)
        succeeded, failed = importer.importArchive(archive, title, recreate)
except archivefileimport.BadZipfile, e:
    msg = 'Something bad with the zipfile; ' + str(e)
    message_type='alert'
else:
    msg = []
    message_type='feedback'
    if succeeded:    
        msg.append('added %s' % view.quotify_list(succeeded))
    else:
        message_type='alert'

    if failed:
        msg.append('<span class="warning">could not add: %s</span>' % view.quotify_list(failed))
    msg = ' '.join(msg)

return view.tab_edit(
    message_type=message_type, message='Finished importing: %s' % msg)
