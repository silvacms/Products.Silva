from Products.Silva.adapters import archivefileimport, zipfileimport
from Products.Silva.i18n import translate as _

view = context
request = view.REQUEST
model = request.model

archive = request.get('importfile', None)
if archive is None or not archive:
    return view.tab_edit_import(
        message_type='error', message=_('Select a file for upload.'))
        

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
    msg = unicode(_('Something bad with the zipfile;')) + ' ' + str(e)
    message_type='alert'
else:
    msg = []
    message_type='feedback'
    if succeeded:  
        message = _('added ${succeeded}')
        message.set_mapping({'succeeded': view.quotify_list(succeeded)})
        msg.append(unicode(message))
    else:
        message_type='alert'

    if failed:
        message = _('<span class="warning">could not add: ${failed}</span>')
        message.set_mapping({'failed': view.quotify_list(failed)})
        msg.append(unicode(message))
    msg = ' '.join(msg)

return view.tab_edit(
    message = _('Finished importing: ${msg}')
    message.set_mapping({'msg': msg})
    message_type=message_type, message=message)
