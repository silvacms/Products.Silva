# Python
from zipfile import ZipFile, BadZipfile
try: from cStringIO import StringIO
except: from StringIO import StringIO
# Zope imports
from OFS.content_types import guess_content_type

        
def import_archive_helper(context, file, title):
    try:
        zip = ZipFile(file)
    except BadZipfile, bzf:
        return bzf

    # Lists the names of the files in the archive which were succesfully 
    # added (or, if not, if something went wrong, list it in failed_list).
    succeeded_list = []
    failed_list = []

    name_list = zip.namelist()
    for name in name_list:
        extracted_file = StringIO(zip.read(name))

        guessed_type, enc = guess_content_type(name)
        if guessed_type.startswith('image'):
            factory = context.manage_addProduct['Silva'].manage_addImage
        else:
            factory = context.manage_addProduct['Silva'].manage_addFile

        # Actually add object; factories return None upon failure
        # FIXME: can I extract some info for the reason of failure?
        added_object = factory(name, title, extracted_file)
        if added_object:
            succeeded_list.append(name)
        else:
            failed_list.append(name)

    return succeeded_list, failed_list
