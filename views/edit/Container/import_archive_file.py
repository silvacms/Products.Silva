from Products.Silva.adapters import archivefileimport, zipfileimport
from Products.Silva.i18n import translate as _
from zope.i18n import translate

view = context
request = view.REQUEST
model = request.model

archive = request.get('importfile', None)
if archive is None or not archive:
    return view.tab_edit_import(
        message_type='error', message=_('Select a file for upload.'))
        

recreate = request.get('recreate_dirs', None)
replace = request.get('replace_content', False)
title = unicode(request.get('title', ''), 'utf-8')
importer = zipfileimport.getZipfileImportAdapter(model)
fullmedia = importer.isFullmediaArchive(archive)

try:
    if fullmedia:
        succeeded, failed = importer.importFromZip(model, archive,  replace)
    else:
        importer = archivefileimport.getArchiveFileImportAdapter(model)
        succeeded, failed = importer.importArchive(
            archive, title, recreate, replace)
except archivefileimport.BadZipfile, e:
    msg = translate(_('Something bad with the zipfile;')) + ' ' + str(e)
    message_type='alert'
else:
    msg = []
    message_type='feedback'
    if succeeded:  
        message = _('added ${succeeded}',
                    mapping={'succeeded': view.quotify_list(succeeded)})
        msg.append(translate(message))
    else:
        message_type='alert'

    if failed:
        message = _('<span class="warning">could not add: ${failed}</span>',
                    mapping={'failed': view.quotify_list(failed)})
        msg.append(translate(message))
    msg = ' '.join(msg)

message = _('Finished importing: ${msg}', mapping={'msg': msg})
return view.tab_edit(message_type=message_type, message=message)
