# Python
from zipfile import ZipFile, BadZipfile
try: from cStringIO import StringIO
except: from StringIO import StringIO
# Zope imports
from OFS.content_types import guess_content_type
# Silva interfaces
from interfaces import IContainer, IAsset
# Silva
import mangle

def import_archive_helper(context, file, title, recreate_dirs=1):
    try:
        zip = ZipFile(file)
    except BadZipfile, bzf:
        return bzf

    # Lists the names of the files in the archive which were succesfully 
    # added (or, if not, if something went wrong, list it in failed_list).
    succeeded_list = []
    failed_list = []

    # Extract filenames, not directories (where name ends with a slash).
    namelist = zip.namelist()
    namelist = [name for name in namelist if name[-1] != '/']

    for name in namelist:
        extracted_file = StringIO(zip.read(name))
        guessed_type, enc = guess_content_type(name)
        
        if not recreate_dirs:
            filename = name
            container = context
        else:
            # Split path into filename and directories.
            path = name.split('/')
            dirs, filename = path[:-1], path[-1]

            container = _find_silva_folder(context, dirs)
            if container is None:
                failed_list.append('/'.join(dirs))
                break

        if guessed_type.startswith('image'):
            factory = container.manage_addProduct['Silva'].manage_addImage
        else:
            factory = container.manage_addProduct['Silva'].manage_addFile

        # Make filename valid and unique.
        assetId = mangle.Id(
            container, filename, file=extracted_file, interface=IAsset)
        assetId.cook().unique()
        if not assetId.isValid():
            failed_list.append(filename)
            continue
        # Actually add object...
        asset_id = str(assetId)
        added_object = factory(asset_id, title, extracted_file)
        # ...successfully? Factories return None upon failure.
        # FIXME: can I extract some info for the reason of failure?
        if added_object is not None:
            added_object.sec_update_last_author_info()
            succeeded_list.append(name)
        else:
            failed_list.append(name)

    return succeeded_list, failed_list

def _find_silva_folder(context, dirs):
    # Create Silva Folder(s) where needed.
    container = context
    for dir in dirs:
        folderId = mangle.Id(
            container, dir, interface=IContainer, allow_dup=1)
        folderId.cook()
        if not folderId.isValid():            
            return None

        objectIds = container.objectIds()
        folder_id = str(folderId)
        if not dir in objectIds:
            # Manage add silva folder.
            obj = _add_silva_folder_helper(container, folder_id)
        else:
            obj = container[folder_id]
            while not IContainer.isImplementedBy(obj):
                # Obj not a silva container, find a new id. Uses an
                # existing Silva Folder if it matches this new id.
                folderId.new()
                folder_id = str(folderId)
                if not folder_id in objectIds:
                    obj = _add_silva_folder_helper(container, folder_id)
                else:
                    obj = container[folder_id]
        # Found or made an container, use that for next directory level.
        container = obj
    return container

def _add_silva_folder_helper(context, id):
    context.manage_addProduct['Silva'].manage_addFolder(id, id)
    return context[id]
