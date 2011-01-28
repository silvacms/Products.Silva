# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import mimetypes
import os
import urllib

# Zope
import zope.deferredimport

# Silva core
from silva.core import interfaces

# Load mime.types
mimetypes.init()


def create_new_filename(file, basename):
    """Compute and set a new filename for an file. It is composed of
    the given id, basename, where the file extension is changed in
    order to match the format of the file.
    """
    if not file.get_file_size():
        return
    extension = None
    if '.' in basename:
        basename, extension = os.path.splitext(basename)
        extension = '.' + extension
    guessed_extension = mimetypes.guess_extension(file.content_type())
    if guessed_extension is not None:
        extension = guessed_extension
    if extension is not None:
        basename += extension
    file.set_filename(basename)


zope.deferredimport.deprecated(
    'Please import directly from silva.core.conf.utils '
    'this import will be removed in Silva 2.4',
    register_service='silva.core.conf.utils:registerService',
    unregister_service='silva.core.conf.utils:unregisterService')


def add_and_edit(self, id, REQUEST, screen='manage_main'):
    """Helper function to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST.has_key('submit_edit'):
        u = "%s/%s" % (u, urllib.quote(id))
        REQUEST.RESPONSE.redirect(u+'/'+screen)
    else:
        REQUEST.RESPONSE.redirect(u+'/manage_main')

def unapprove_close_helper(object):
    """Unapprove/close object and anything unapprovable/closeable
    contained by it.
    """
    if interfaces.IVersioning.providedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
        if object.is_version_published():
            object.close_version()
    if interfaces.IContainer.providedBy(object):
        default = object.get_default()
        if default:
            unapprove_close_helper(default)
        for item in object.get_ordered_publishables():
            unapprove_close_helper(item)


def fix_content_type_header(uploaded_file):
    """Deletes the content-type header on the uploaded_file.

    This ensures consistent mimetype assignment for the Silva application
    since Zope will now fallback to the Python database for resolving
    a mimetype.
    """
    if hasattr(uploaded_file, 'headers'):
        if uploaded_file.headers.has_key('content-type'):
            del uploaded_file.headers['content-type']



# this class used to be in SilvaDocument.upgrade, but was moved
# here when Folder._to_folder_or_publication_helper began using it.
class SwitchClass(object):
    """This class can be used to switch an instances class.
       This was used when SilvaDocument was moved to it's own
       product, to switch instances of SilvaDocument and Silva
       Document Version from Products.Silva.Document.Document and
       Products.Silva.Document.DocumentVersion to Products.SilvaDocument.
       Document.Document and DocumentVersion.

       This is also used by Folder._to_folder_or_publication_helper
       to switch a container between folders and publications

       This class conforms to the Silva upgrader API, in that you
       call class.upgrade(obj) to upgrade obj, and the upgraded
       obj is returned"""

    def __init__(self, new_class, args=(), kwargs={}):
        self.new_class = new_class
        self.args = args
        self.kwargs = kwargs

    def upgrade(self, obj):
        obj_id = obj.getId()
        new_obj = self.new_class(obj_id, *self.args, **self.kwargs)
        new_obj.__dict__.update(obj.__dict__)
        container = obj.aq_parent
        #remove old object (since this is
        # just replacing the object, we can suppress events)
        container._delObject(obj_id, suppress_events=True)
        #make sure _setObject is used, and not setattr,
        # as ObjectManagers maintain extra data structures
        # about contained objects
        container._setObject(obj_id, new_obj, suppress_events=True)
        return getattr(container, obj_id)

    def __repr__(self):
        return "<SwitchClass %r>" % self.new_class
